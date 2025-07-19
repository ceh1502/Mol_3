const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const passport = require('../config/passport');
const Player = require('../models/Player');
const router = express.Router();

const JWT_SECRET = process.env.JWT_SECRET || 'minecraft-game-secret-key';

// 일반 회원가입
router.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    
    // 입력값 검증
    if (!username || !email || !password) {
      return res.status(400).json({ error: '모든 필드를 입력해주세요.' });
    }
    
    if (password.length < 6) {
      return res.status(400).json({ error: '비밀번호는 6자 이상이어야 합니다.' });
    }
    
    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ error: '올바른 이메일 형식이 아닙니다.' });
    }
    
    // 기존 사용자 확인
    const existingPlayer = await Player.findOne({ email: email });
    
    if (existingPlayer) {
      return res.status(400).json({ error: '이미 사용 중인 이메일입니다.' });
    }
    
    // 비밀번호 해싱
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // 새 플레이어 생성
    const player = new Player({
      email: email,
      name: username,
      password: hashedPassword,
      profilePicture: '/images/characters/avatar_down.png',
      score: 0,
      gamesPlayed: 0
    });
    
    await player.save();
    
    // JWT 토큰 생성
    const token = jwt.sign(
      { 
        id: player._id,
        email: player.email,
        name: player.name
      },
      JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    res.status(201).json({
      success: true,
      message: '회원가입이 완료되었습니다.',
      token: token,
      user: {
        id: player._id,
        name: player.name,
        email: player.email,
        profilePicture: player.profilePicture,
        score: player.score,
        gamesPlayed: player.gamesPlayed
      }
    });
    
  } catch (error) {
    console.error('❌ 회원가입 에러:', error);
    res.status(500).json({ error: '서버 에러가 발생했습니다.' });
  }
});

// 일반 로그인
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    // 입력값 검증
    if (!username || !password) {
      return res.status(400).json({ error: '사용자명과 비밀번호를 입력해주세요.' });
    }
    
    // 사용자 찾기 (이메일 또는 사용자명으로 로그인 가능)
    const player = await Player.findOne({ 
      $or: [
        { email: username },
        { name: username }
      ]
    });
    
    if (!player) {
      return res.status(401).json({ error: '사용자를 찾을 수 없습니다.' });
    }
    
    // 구글 로그인 사용자는 일반 로그인 불가
    if (player.googleId && !player.password) {
      return res.status(401).json({ error: '구글 계정으로 로그인해주세요.' });
    }
    
    // 비밀번호 확인
    const isPasswordValid = await bcrypt.compare(password, player.password);
    if (!isPasswordValid) {
      return res.status(401).json({ error: '비밀번호가 일치하지 않습니다.' });
    }
    
    // JWT 토큰 생성
    const token = jwt.sign(
      { 
        id: player._id,
        email: player.email,
        name: player.name
      },
      JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    res.json({
      success: true,
      message: '로그인이 완료되었습니다.',
      token: token,
      user: {
        id: player._id,
        name: player.name,
        email: player.email,
        profilePicture: player.profilePicture,
        score: player.score,
        gamesPlayed: player.gamesPlayed
      }
    });
    
  } catch (error) {
    console.error('❌ 로그인 에러:', error);
    res.status(500).json({ error: '서버 에러가 발생했습니다.' });
  }
});

// Google OAuth 시작
router.get('/google',
  passport.authenticate('google', { scope: ['profile', 'email'] })
);

// Google OAuth 콜백
router.get('/google/callback',
  passport.authenticate('google', { session: false }),
  (req, res) => {
    try {
      // JWT 토큰 생성
      const token = jwt.sign(
        { 
          id: req.user.id, 
          googleId: req.user.googleId,
          email: req.user.email,
          name: req.user.name
        },
        JWT_SECRET,
        { expiresIn: '7d' }
      );

      // 프론트엔드로 리다이렉트 (토큰 포함)
      res.redirect(`http://localhost:3000?token=${token}&user=${encodeURIComponent(JSON.stringify({
        id: req.user.id,
        name: req.user.name,
        email: req.user.email,
        profilePicture: req.user.profilePicture,
        score: req.user.score
      }))}`);
    } catch (error) {
      console.error('❌ OAuth 콜백 에러:', error);
      res.redirect('http://localhost:3000?error=auth_failed');
    }
  }
);

// 토큰 검증
router.get('/verify', passport.authenticate('jwt', { session: false }), (req, res) => {
  res.json({
    success: true,
    user: {
      id: req.user.id,
      name: req.user.name,
      email: req.user.email,
      profilePicture: req.user.profilePicture,
      score: req.user.score,
      gamesPlayed: req.user.gamesPlayed
    }
  });
});

// 로그아웃
router.post('/logout', (req, res) => {
  res.json({ success: true, message: '로그아웃 완료' });
});

// 사용자 정보 업데이트
router.put('/user', passport.authenticate('jwt', { session: false }), async (req, res) => {
  try {
    const { name } = req.body;
    const player = req.user;
    
    if (name) {
      player.name = name;
      await player.save();
    }
    
    res.json({
      success: true,
      user: {
        id: player.id,
        name: player.name,
        email: player.email,
        profilePicture: player.profilePicture,
        score: player.score,
        gamesPlayed: player.gamesPlayed
      }
    });
  } catch (error) {
    console.error('❌ 사용자 정보 업데이트 에러:', error);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

module.exports = router;