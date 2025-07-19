# Google OAuth 2.0 설정 가이드

## 1. Google Cloud Console 설정

### 1.1 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택

### 1.2 OAuth 2.0 API 설정
1. **API 및 서비스** > **사용자 인증 정보** 이동
2. **+ 사용자 인증 정보 만들기** > **OAuth 2.0 클라이언트 ID** 선택
3. **웹 애플리케이션** 선택

### 1.3 승인된 리디렉션 URI 설정
**개발 환경에서는 localhost만 추가:**
```
http://localhost:5001/auth/google/callback
http://127.0.0.1:5001/auth/google/callback
```

**⚠️ 중요**: Google OAuth는 IP 주소를 직접 허용하지 않습니다. 
- 개발: localhost 사용
- 프로덕션: 실제 도메인 필요 (예: https://yourdomain.com)

### 1.4 승인된 자바스크립트 원본 설정
**개발 환경에서는 localhost만 추가:**
```
http://localhost:3000
http://localhost:5001
http://127.0.0.1:3000
http://127.0.0.1:5001
```

## 2. OAuth 동의 화면 설정

### 2.1 기본 정보
- **앱 이름**: Minecraft 2D Game
- **사용자 지원 이메일**: 본인 이메일
- **개발자 연락처 정보**: 본인 이메일

### 2.2 범위 설정
다음 범위들을 추가:
- `userinfo.email`
- `userinfo.profile`

### 2.3 테스트 사용자 추가 (개발 중)
- **OAuth 동의 화면** > **테스트 사용자** 
- 테스트할 Google 계정 이메일 추가

## 3. 환경변수 설정

`.env` 파일에 발급받은 클라이언트 ID와 시크릿 추가:

```env
GOOGLE_CLIENT_ID=your-actual-client-id.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret

# OAuth 콜백 URL 설정 (자동 환경 감지 지원)
OAUTH_CALLBACK_URL_LOCAL=http://localhost:5001/auth/google/callback
OAUTH_CALLBACK_URL_NETWORK=http://143.248.162.5:5001/auth/google/callback

# 네트워크 환경 설정 (선택사항)
NETWORK_HOST=143.248.162.5
```

## 4. 개발 환경에서 테스트

### 4.1 앱 게시 상태
- 개발 중에는 **테스트** 상태로 유지
- 테스트 사용자만 로그인 가능

### 4.2 프로덕션 배포 시
- **게시** 상태로 변경
- Google 검토 과정 필요 (몇 일 소요)

## 5. 일반적인 문제 해결

### 5.1 "앱이 차단됨" 오류
- OAuth 동의 화면에서 테스트 사용자에 본인 이메일 추가
- 앱 상태가 "테스트"인지 확인

### 5.2 "리디렉션 URI 불일치" 오류
- 콜백 URL이 정확히 설정되었는지 확인
- HTTP/HTTPS 프로토콜 일치 확인

### 5.3 "클라이언트 ID 오류"
- 환경변수가 올바르게 설정되었는지 확인
- 서버 재시작 후 테스트

## 6. 환경별 접근 방법

### 6.1 로컬 개발 환경
- URL: `http://localhost:3000`
- OAuth 콜백: `http://localhost:5001/auth/google/callback`
- ✅ Google OAuth 사용 가능

### 6.2 네트워크 환경 (다른 컴퓨터에서 접근)
- URL: `http://143.248.162.5:3000` (서버 IP 사용)
- ❌ Google OAuth 사용 불가 (IP 주소 제한)
- ✅ 게스트 로그인 사용 권장

### 6.3 프로덕션 환경
- 실제 도메인 필요 (예: https://yourgame.com)
- HTTPS 필수
- ✅ Google OAuth 정상 작동

## 7. 임시 해결책

Google OAuth 설정이 완료되기 전까지는 **게스트 로그인**을 사용하여 게임을 테스트할 수 있습니다.

게스트 로그인으로도 모든 게임 기능을 사용할 수 있으며, 랭킹 시스템도 완전히 작동합니다.