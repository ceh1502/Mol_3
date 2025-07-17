# 🎵 Rhythm Game Frontend

React TypeScript로 구현된 리듬게임 프론트엔드입니다.

## 🎮 게임 특징

- **4개 레인**: A, S, K, L 키로 플레이
- **실시간 판정**: Perfect, Great, Good, Miss 판정 시스템
- **점수 및 콤보**: 실시간 점수 계산 및 콤보 표시
- **반응형 UI**: 아름다운 네온 스타일 디자인

## 🎯 게임 플레이

1. **Start** 버튼을 클릭하여 게임 시작
2. 노트가 히트 존에 도달할 때 해당 키를 누르세요:
   - **A**: 첫 번째 레인 (빨간색)
   - **S**: 두 번째 레인 (초록색)
   - **K**: 세 번째 레인 (파란색)
   - **L**: 네 번째 레인 (노란색)

## 🏆 점수 시스템

- **Perfect**: 100점 (금색)
- **Great**: 80점 (녹색)
- **Good**: 60점 (파란색)
- **Miss**: 0점 (빨간색)

## 🚀 실행 방법

### 개발 모드
```bash
npm start
```

### 프로덕션 빌드
```bash
npm run build
```

### 테스트 실행
```bash
npm test
```

## 📁 프로젝트 구조

```
src/
├── components/
│   ├── GameArea.tsx       # 메인 게임 영역
│   ├── Lane.tsx           # 개별 레인 컴포넌트
│   ├── Note.tsx           # 노트 컴포넌트
│   ├── ScoreBoard.tsx     # 점수판 컴포넌트
│   └── *.css              # 스타일 파일들
├── types/
│   └── game.ts            # 게임 타입 정의
├── App.tsx                # 메인 앱 컴포넌트
└── index.tsx              # 진입점
```

## 🎨 기술 스택

- **React 18** with TypeScript
- **CSS3** with animations
- **Web API** for keyboard events
- **Responsive Design**

## 🔧 주요 기능

### 게임 엔진
- 실시간 노트 생성 및 이동
- 키보드 입력 처리
- 충돌 감지 및 판정
- 점수 계산 시스템

### UI/UX
- 네온 스타일 디자인
- 부드러운 애니메이션
- 반응형 레이아웃
- 실시간 피드백

## 🎵 향후 개발 계획

- [ ] 음악 파일 로딩 기능
- [ ] 비트맵 에디터
- [ ] 백엔드 API 연동
- [ ] 사용자 설정 저장
- [ ] 다양한 게임 모드
- [ ] 온라인 리더보드

## 🤝 기여하기

1. 이 리포지토리를 포크하세요
2. 기능 브랜치를 생성하세요 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성하세요

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.