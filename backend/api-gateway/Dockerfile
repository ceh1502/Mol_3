# Node.js API Gateway Dockerfile
# 유튜브 URL 처리 및 작업 큐 관리를 위한 Express 서버 컨테이너
FROM node:18-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 도구 설치
RUN apk update && apk add --no-cache \
    python3 \
    make \
    g++ \
    git \
    curl

# package.json과 package-lock.json 복사 (캐시 최적화)
COPY package*.json ./

# 의존성 설치
RUN npm ci --only=production

# 애플리케이션 코드 복사
COPY src/ ./src/

# 비특권 사용자 생성 및 전환 (보안)
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# 앱 디렉토리 소유권 변경
RUN chown -R nextjs:nodejs /app
USER nextjs

# 포트 노출
EXPOSE 3000

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# 애플리케이션 시작
CMD ["npm", "start"]