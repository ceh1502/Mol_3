const express = require('express');
const Player = require('../models/Player');
const passport = require('../config/passport');
const router = express.Router();

// 랭킹 조회 (DB + 메모리 게스트 랭킹 통합)
router.get('/', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 10;
    
    // 데이터베이스 플레이어
    const topPlayers = await Player.getTopPlayers(limit);
    const dbRanking = topPlayers.map(player => ({
      id: player.id,
      name: player.name,
      profilePicture: player.profilePicture,
      score: player.score,
      gamesPlayed: player.gamesPlayed,
      isGuest: false
    }));
    
    // 게스트 플레이어 (전역 변수에서 가져오기)
    const guestRanking = global.guestRanking ? Array.from(global.guestRanking.values()) : [];
    
    // 통합 랭킹 (점수 순으로 정렬)
    const combinedRanking = [...dbRanking, ...guestRanking]
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
    
    res.json({
      success: true,
      ranking: combinedRanking.map((player, index) => ({
        rank: index + 1,
        id: player.id,
        name: player.name,
        profilePicture: player.profilePicture,
        score: player.score,
        gamesPlayed: player.gamesPlayed || 0,
        isGuest: player.isGuest || false
      }))
    });
  } catch (error) {
    console.error('❌ 랭킹 조회 에러:', error);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// 특정 플레이어 랭킹 조회
router.get('/player/:id', async (req, res) => {
  try {
    const playerId = req.params.id;
    const player = await Player.findByPk(playerId);
    
    if (!player) {
      return res.status(404).json({ success: false, message: '플레이어를 찾을 수 없습니다' });
    }
    
    // 해당 플레이어보다 점수가 높은 플레이어 수 계산 (랭킹)
    const higherScorePlayers = await Player.count({
      where: {
        score: {
          [require('sequelize').Op.gt]: player.score
        }
      }
    });
    
    const rank = higherScorePlayers + 1;
    
    res.json({
      success: true,
      player: {
        rank: rank,
        id: player.id,
        name: player.name,
        profilePicture: player.profilePicture,
        score: player.score,
        gamesPlayed: player.gamesPlayed
      }
    });
  } catch (error) {
    console.error('❌ 플레이어 랭킹 조회 에러:', error);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// 점수 추가 (인증된 사용자만)
router.post('/add-score', passport.authenticate('jwt', { session: false }), async (req, res) => {
  try {
    const { points = 1 } = req.body;
    const player = req.user;
    
    const newScore = await player.addScore(points);
    
    // 새로운 랭킹 계산
    const higherScorePlayers = await Player.count({
      where: {
        score: {
          [require('sequelize').Op.gt]: newScore
        }
      }
    });
    
    const rank = higherScorePlayers + 1;
    
    res.json({
      success: true,
      newScore: newScore,
      rank: rank,
      pointsAdded: points
    });
  } catch (error) {
    console.error('❌ 점수 추가 에러:', error);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// 통계 조회
router.get('/stats', async (req, res) => {
  try {
    const totalPlayers = await Player.count();
    const totalGames = await Player.sum('gamesPlayed');
    const highestScore = await Player.max('score');
    const averageScore = await Player.findOne({
      attributes: [
        [require('sequelize').fn('AVG', require('sequelize').col('score')), 'avgScore']
      ]
    });
    
    res.json({
      success: true,
      stats: {
        totalPlayers,
        totalGames: totalGames || 0,
        highestScore: highestScore || 0,
        averageScore: Math.round(averageScore?.dataValues?.avgScore || 0)
      }
    });
  } catch (error) {
    console.error('❌ 통계 조회 에러:', error);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

module.exports = router;