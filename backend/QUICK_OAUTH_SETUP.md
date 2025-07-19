# 🚀 빠른 Google OAuth 설정 가이드

## 1. Google Cloud Console 설정 (5분)

### 1.1 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성: "Minecraft-2D-Game"

### 1.2 OAuth 2.0 설정
1. **API 및 서비스** > **사용자 인증 정보** 이동
2. **+ 사용자 인증 정보 만들기** > **OAuth 2.0 클라이언트 ID**
3. **웹 애플리케이션** 선택

### 1.3 URI 설정
**승인된 리디렉션 URI에 추가:**
```
http://localhost:5001/auth/google/callback
http://127.0.0.1:5001/auth/google/callback
https://minecrafton.store/auth/google/callback
```

**승인된 자바스크립트 원본에 추가:**
```
http://localhost:3000
http://localhost:5001
http://127.0.0.1:3000
http://127.0.0.1:5001
https://minecrafton.store
```

**✅ 지원 도메인**: localhost (개발), minecrafton.store (프로덕션)

### 1.4 OAuth 동의 화면
1. **OAuth 동의 화면** 설정
2. **외부** 선택 (개인 사용)
3. **앱 이름**: "Minecraft 2D Game"
4. **사용자 지원 이메일**: 본인 이메일
5. **저장 후 계속**

## 2. 환경변수 설정 (1분)

`.env` 파일에서 다음 값들을 실제 값으로 변경:

```env
# 발급받은 실제 값으로 변경
GOOGLE_CLIENT_ID=1234567890-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
```

## 3. 서버 재시작

```bash
# 서버 종료 후 재시작
node server.js
```

## 4. 테스트

1. 브라우저에서 `http://localhost:3000` 접속
2. "Google로 로그인" 버튼 활성화 확인
3. Google 계정으로 로그인 테스트

---

**⚠️ 참고**: 현재는 게스트 로그인으로도 모든 기능을 사용할 수 있습니다!