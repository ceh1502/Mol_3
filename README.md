# 🎵 Rhythm Game Project

AI 기반 리듬게임 프로젝트입니다.

## 📁 프로젝트 구조
```
Mol_3/
├── backend/           # 백엔드 서비스
│   ├── ai-service/    # AI 비트맵 생성 서비스
│   ├── api-gateway/   # API 게이트웨이 서비스
│   └── docker-compose.yml
├── frontend/          # 프론트엔드 애플리케이션
└── README.md
```

## 🎯 주요 기능
- **유튜브 오디오 추출**: yt-dlp를 통한 고품질 오디오 다운로드
- **GPU 기반 오디오 분석**: 딥러닝 모델을 활용한 비트, 템포, 온셋 검출
- **자동 비트맵 생성**: 난이도별 게임 노트 자동 생성
- **리듬게임 플레이 인터페이스**: 사용자 친화적인 게임 UI
- **실시간 처리**: Redis 기반 작업 큐 시스템

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│  API Gateway    │───▶│   AI Service    │
│   (React/Vue)   │    │   (Node.js)     │    │   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                         ┌─────────────┐         ┌─────────────┐
                         │   Redis     │         │ GPU 모델    │
                         │   Queue     │         │ 오디오 분석  │
                         └─────────────┘         └─────────────┘
```

## 🚀 개발 환경 설정

### 전체 시스템 실행
```bash
# 백엔드 서비스 시작
cd backend
docker-compose up -d

# 프론트엔드 개발 서버 시작
cd frontend
npm install
npm run dev
```

### 개별 서비스 실행
각 서비스별 README를 참조하세요:
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)

## 🔧 API 사용법

### 유튜브 비트맵 생성 요청
```bash
curl -X POST http://localhost:3000/api/youtube/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "difficulty": "normal"
  }'
```

### 비트맵 결과 조회
```bash
curl http://localhost:3000/api/beatmap/{jobId}
```

## 🎛️ 난이도 레벨
- `easy`: 낮은 노트 밀도, 단순한 패턴
- `normal`: 보통 밀도, 기본 패턴
- `hard`: 높은 밀도, 복잡한 패턴
- `expert`: 매우 높은 밀도, 고급 패턴

## 🤝 기여하기

1. Fork 프로젝트
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.