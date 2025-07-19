const mongoose = require('mongoose');

// Player 스키마 정의
const playerSchema = new mongoose.Schema({
  googleId: {
    type: String,
    unique: true,
    sparse: true, // null 값 허용하면서 unique 제약 조건 적용
    comment: 'Google OAuth ID'
  },
  password: {
    type: String,
    comment: '일반 로그인 비밀번호 (해싱됨)'
  },
  email: {
    type: String,
    required: true,
    unique: true,
    validate: {
      validator: function(v) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
      },
      message: '올바른 이메일 형식이 아닙니다'
    }
  },
  name: {
    type: String,
    required: true
  },
  profilePicture: {
    type: String,
    default: '/images/characters/avatar_down.png',
    comment: '프로필 이미지 URL'
  },
  score: {
    type: Number,
    default: 0,
    comment: '좀비 킬 점수'
  },
  gamesPlayed: {
    type: Number,
    default: 0,
    comment: '플레이한 게임 수'
  },
  lastPlayed: {
    type: Date,
    comment: '마지막 플레이 날짜'
  }
}, {
  timestamps: true, // createdAt, updatedAt 자동 생성
  collection: 'players'
});

// 인덱스 설정
playerSchema.index({ googleId: 1 });
playerSchema.index({ email: 1 });
playerSchema.index({ score: -1 }); // 점수 내림차순 정렬용

// 스태틱 메서드 - 상위 플레이어 조회
playerSchema.statics.getTopPlayers = async function(limit = 10) {
  return await this.find({}, 'name profilePicture score gamesPlayed')
    .sort({ score: -1 })
    .limit(limit);
};

// 인스턴스 메서드 - 점수 추가
playerSchema.methods.addScore = async function(points = 1) {
  this.score += points;
  await this.save();
  return this.score;
};

// 인스턴스 메서드 - 게임 플레이 횟수 증가
playerSchema.methods.incrementGamesPlayed = async function() {
  this.gamesPlayed += 1;
  this.lastPlayed = new Date();
  await this.save();
};

// 모델 생성
const Player = mongoose.model('Player', playerSchema);

module.exports = Player;