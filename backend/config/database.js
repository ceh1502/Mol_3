const mongoose = require('mongoose');

// MongoDB 연결 설정
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/minecraft2d';

// MongoDB 연결
async function connectToMongoDB() {
  try {
    await mongoose.connect(MONGODB_URI, {
      
      
    });
    console.log('✅ MongoDB 연결 성공');
  } catch (error) {
    console.error('❌ MongoDB 연결 실패:', error);
    process.exit(1);
  }
}

// 연결 이벤트 리스너
mongoose.connection.on('connected', () => {
  console.log('🔗 Mongoose가 MongoDB에 연결되었습니다');
});

mongoose.connection.on('error', (err) => {
  console.error('❌ MongoDB 연결 오류:', err);
});

mongoose.connection.on('disconnected', () => {
  console.log('🔌 MongoDB 연결이 해제되었습니다');
});

// 프로세스 종료 시 연결 해제
process.on('SIGINT', async () => {
  await mongoose.connection.close();
  console.log('👋 MongoDB 연결이 앱 종료로 인해 해제되었습니다');
  process.exit(0);
});

module.exports = { connectToMongoDB, mongoose };