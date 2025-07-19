# 🌐 minecrafton.store 도메인 Google OAuth 설정 가이드

## 1. Google Cloud Console 설정

### 1.1 프로젝트 생성 또는 선택
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성: "Minecraft-2D-Game" 또는 기존 프로젝트 선택

### 1.2 OAuth 2.0 클라이언트 ID 생성
1. **API 및 서비스** > **사용자 인증 정보** 이동
2. **+ 사용자 인증 정보 만들기** > **OAuth 2.0 클라이언트 ID**
3. **웹 애플리케이션** 선택
4. 이름: "Minecraft 2D Game - Web Client"

### 1.3 승인된 자바스크립트 원본 설정
다음 원본들을 추가:
```
http://localhost:3000
http://localhost:5001
https://minecrafton.store
https://www.minecrafton.store
```

### 1.4 승인된 리디렉션 URI 설정
다음 URI들을 추가:
```
http://localhost:5001/auth/google/callback
https://minecrafton.store/auth/google/callback
https://www.minecrafton.store/auth/google/callback
```

## 2. OAuth 동의 화면 설정

### 2.1 기본 정보
- **User Type**: 외부 (External)
- **앱 이름**: Minecraft 2D Game
- **사용자 지원 이메일**: 본인 이메일
- **앱 로고**: (선택사항) 게임 로고 업로드
- **앱 도메인**:
  - 홈페이지: `https://minecrafton.store`
  - 개인정보처리방침: `https://minecrafton.store/privacy`
  - 서비스 약관: `https://minecrafton.store/terms`
- **승인된 도메인**: `minecrafton.store`
- **개발자 연락처 정보**: 본인 이메일

### 2.2 범위 설정
다음 범위들을 추가:
- `.../auth/userinfo.email`
- `.../auth/userinfo.profile`

### 2.3 테스트 사용자 (개발 중)
- 테스트할 Google 계정 이메일들을 추가
- 개발 단계에서는 이 사용자들만 로그인 가능

## 3. 환경변수 설정

`.env` 파일에 발급받은 클라이언트 ID와 시크릿을 설정:

```env
# Google OAuth 설정 (실제 값으로 변경)
GOOGLE_CLIENT_ID=1234567890-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz

# 도메인 설정
DOMAIN=minecrafton.store
NODE_ENV=production

# OAuth 콜백 URL 설정
OAUTH_CALLBACK_URL_LOCAL=http://localhost:5001/auth/google/callback
OAUTH_CALLBACK_URL_PRODUCTION=https://minecrafton.store/auth/google/callback
```

## 4. 도메인 SSL 인증서 설정

### 4.1 HTTPS 필수
- Google OAuth는 프로덕션에서 HTTPS를 요구합니다
- Let's Encrypt 또는 기타 SSL 인증서 설정 필요

### 4.2 DNS 설정
- A 레코드: `minecrafton.store` → 서버 IP
- CNAME 레코드: `www.minecrafton.store` → `minecrafton.store`

## 5. 서버 배포 설정

### 5.1 Nginx 프록시 설정 예시
```nginx
server {
    listen 80;
    server_name minecrafton.store www.minecrafton.store;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name minecrafton.store www.minecrafton.store;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # 프론트엔드 (React)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 백엔드 API
    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # OAuth 엔드포인트
    location /auth/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Socket.IO
    location /socket.io/ {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 6. 테스트 단계

### 6.1 로컬 테스트
1. `localhost:3000`에서 게임 접속
2. Google 로그인 버튼 활성화 확인
3. OAuth 플로우 테스트

### 6.2 도메인 테스트
1. `https://minecrafton.store`에서 게임 접속
2. Google 로그인 기능 테스트
3. 로그인 후 게임 기능 확인

## 7. 프로덕션 배포

### 7.1 앱 게시
- OAuth 동의 화면에서 **게시** 상태로 변경
- Google 검토 과정 (1-2주 소요 가능)
- 검토 완료 후 모든 사용자 로그인 가능

### 7.2 모니터링
- OAuth 사용량 모니터링
- 에러 로그 확인
- 사용자 피드백 수집

---

**🎯 목표**: localhost 개발환경과 minecrafton.store 프로덕션 환경 모두에서 Google OAuth 사용 가능!