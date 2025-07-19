// 🔧 환경변수 확인
require('dotenv').config();

const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const JwtStrategy = require('passport-jwt').Strategy;
const ExtractJwt = require('passport-jwt').ExtractJwt;
const Player = require('../models/Player');

// JWT 전략
passport.use(new JwtStrategy({
  jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
  secretOrKey: process.env.JWT_SECRET || 'minecraft-game-secret-key'
}, async (payload, done) => {
  try {
    const player = await Player.findByPk(payload.id);
    if (player) {
      return done(null, player);
    }
    return done(null, false);
  } catch (error) {
    return done(error, false);
  }
}));

// OAuth 콜백 URL (환경별 동적 설정)
const getCallbackURL = () => {
  // 환경변수에서 직접 설정된 콜백 URL 사용
  if (process.env.OAUTH_CALLBACK_URL) {
    return process.env.OAUTH_CALLBACK_URL;
  }
  
  // 프로덕션 환경 (도메인이 설정된 경우)
  if (process.env.NODE_ENV === 'production' || process.env.DOMAIN) {
    return "https://minecrafton.store/auth/google/callback";
  }
  
  // 개발 환경
  return "http://localhost:5001/auth/google/callback";
};

// 환경변수 디버깅
console.log('🔧 Passport 설정 - 환경변수 확인:');
console.log('- CLIENT_ID:', process.env.GOOGLE_CLIENT_ID ? '✅ 설정됨' : '❌ 미설정');
console.log('- CLIENT_SECRET:', process.env.GOOGLE_CLIENT_SECRET ? '✅ 설정됨' : '❌ 미설정');
console.log('- CALLBACK_URL:', getCallbackURL());

// Google OAuth 전략 (필요시에만 활성화)
if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
  passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: getCallbackURL()
  }, async (accessToken, refreshToken, profile, done) => {
    try {
      // 기존 플레이어 찾기
      let player = await Player.findOne({ where: { googleId: profile.id } });
      
      if (player) {
        // 기존 플레이어 정보 업데이트
        player.name = profile.displayName;
        player.email = profile.emails[0].value;
        player.profilePicture = profile.photos[0].value;
        await player.save();
      } else {
        // 새 플레이어 생성
        player = await Player.create({
          googleId: profile.id,
          name: profile.displayName,
          email: profile.emails[0].value,
          profilePicture: profile.photos[0].value
        });
      }
      
      return done(null, player);
    } catch (error) {
      return done(error, null);
    }
  }));
} else {
  console.log('🔧 Google OAuth 설정이 없어 비활성화됨');
}

passport.serializeUser((player, done) => {
  done(null, player.id);
});

passport.deserializeUser(async (id, done) => {
  try {
    const player = await Player.findByPk(id);
    done(null, player);
  } catch (error) {
    done(error, null);
  }
});

module.exports = passport;