// Express 서버 메인 애플리케이션
// 유튜브 URL 처리 및 비트맵 생성 요청을 받는 API Gateway
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');

// 라우터 불러오기
const youtubeRoutes = require('./routes/youtube.routes');
const beatmapRoutes = require('./routes/beatmap.routes');
const healthRoutes = require('./routes/health.routes');

// 미들웨어 불러오기
const errorHandler = require('./middleware/error.middleware');
const validateRequest = require('./middleware/validation.middleware');

const app = express();

// 보안 미들웨어
app.use(helmet());
app.use(cors());

// 로깅 미들웨어
app.use(morgan('combined'));

// 요청 제한 설정 (DDoS 방지)
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15분
  max: 100, // 최대 100개 요청
  message: 'Too many requests from this IP'
});
app.use(limiter);

// 바디 파서
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// 라우트 설정
app.use('/api/youtube', youtubeRoutes);  // 유튜브 URL 처리
app.use('/api/beatmap', beatmapRoutes);  // 비트맵 조회/다운로드
app.use('/api/health', healthRoutes);    // 헬스체크

// 에러 핸들링 미들웨어
app.use(errorHandler);

// 404 처리
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});

module.exports = app;