# 🎵 유튜브 리듬게임 백엔드 시스템

## 📋 프로젝트 개요

유튜브 URL을 입력받아 자동으로 리듬게임 비트맵을 생성하는 GPU 기반 AI 백엔드 시스템입니다.

### 🎯 주요 기능
- **유튜브 오디오 추출**: yt-dlp를 통한 고품질 오디오 다운로드
- **GPU 기반 오디오 분석**: 딥러닝 모델을 활용한 비트, 템포, 온셋 검출
- **자동 비트맵 생성**: 난이도별 게임 노트 자동 생성
- **실시간 처리**: Redis 기반 작업 큐 시스템
- **확장 가능한 아키텍처**: 마이크로서비스 기반 설계

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   프론트엔드    │───▶│  API Gateway    │───▶│   AI Service    │
│   (React/Vue)   │    │   (Node.js)     │    │   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                         ┌─────────────┐         ┌─────────────┐
                         │   Redis     │         │ GPU 모델    │
                         │   Queue     │         │ 오디오 분석  │
                         └─────────────┘         └─────────────┘
```

## 📁 디렉토리 구조

```
rhythm-game-backend/
├── api-gateway/                 # Node.js Express API Gateway
│   ├── src/
│   │   ├── controllers/         # HTTP 요청 처리 컨트롤러
│   │   │   ├── youtube.controller.js    # 유튜브 URL 처리
│   │   │   └── beatmap.controller.js    # 비트맵 조회/다운로드
│   │   ├── services/            # 비즈니스 로직 서비스
│   │   │   ├── youtubeService.js        # 유튜브 메타데이터 추출
│   │   │   ├── aiService.js             # AI 서비스 통신
│   │   │   └── queueService.js          # Redis 큐 관리
│   │   ├── models/              # 데이터 모델
│   │   ├── routes/              # API 라우트 정의
│   │   ├── middleware/          # Express 미들웨어
│   │   └── app.js               # Express 애플리케이션 진입점
│   ├── package.json             # Node.js 의존성 및 스크립트
│   └── Dockerfile               # API Gateway 컨테이너 설정
├── ai-service/                  # Python FastAPI AI Service
│   ├── src/
│   │   ├── audio/               # 오디오 처리 모듈
│   │   │   ├── youtube_downloader.py    # yt-dlp 오디오 다운로드
│   │   │   ├── audio_processor.py       # 오디오 전처리
│   │   │   └── format_converter.py      # 포맷 변환
│   │   ├── models/              # AI 모델 및 분석
│   │   │   ├── beat_tracker.py          # GPU 비트 추출
│   │   │   ├── onset_detector.py        # 음표 시작점 검출
│   │   │   └── tempo_estimator.py       # BPM 추정
│   │   ├── beatmap/             # 비트맵 생성
│   │   │   ├── generator.py             # 게임 맵 생성 알고리즘
│   │   │   └── difficulty_calculator.py # 난이도 계산
│   │   ├── api/                 # FastAPI 엔드포인트
│   │   ├── utils/               # 유틸리티 함수
│   │   └── main.py              # FastAPI 애플리케이션 진입점
│   ├── requirements.txt         # Python 의존성
│   └── Dockerfile.gpu           # GPU 지원 컨테이너 설정
├── docker-compose.yml           # 전체 시스템 오케스트레이션
└── README.md                    # 프로젝트 문서
```

## 🚀 시작하기

### 필요 조건
- Docker & Docker Compose
- NVIDIA GPU (CUDA 11.8+ 지원)
- Node.js 18+ (로컬 개발 시)
- Python 3.9+ (로컬 개발 시)

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd rhythm-game-backend
```

### 2. 환경 설정
```bash
# API Gateway 환경 변수
cp api-gateway/.env.example api-gateway/.env

# AI Service 환경 변수
cp ai-service/.env.example ai-service/.env
```

### 3. Docker로 전체 시스템 실행
```bash
# 전체 시스템 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f api-gateway
docker-compose logs -f ai-service
```

### 4. 개발 모드 실행
```bash
# API Gateway 개발 모드
cd api-gateway
npm install
npm run dev

# AI Service 개발 모드
cd ai-service
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 API 사용법

### 1. 유튜브 비트맵 생성 요청
```bash
curl -X POST http://localhost:3000/api/youtube/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "difficulty": "normal"
  }'
```

**응답:**
```json
{
  "jobId": "job_12345",
  "status": "processing",
  "estimatedTime": 45,
  "metadata": {
    "title": "Never Gonna Give You Up",
    "duration": 213,
    "uploader": "RickAstleyVEVO"
  }
}
```

### 2. 비트맵 결과 조회
```bash
curl http://localhost:3000/api/beatmap/job_12345
```

**응답:**
```json
{
  "status": "completed",
  "beatmap": {
    "bpm": 128,
    "duration": 213,
    "notes": [
      {"time": 0.5, "lane": 0, "type": "tap"},
      {"time": 1.0, "lane": 2, "type": "hold", "duration": 0.5}
    ]
  },
  "metadata": {
    "difficulty": "normal",
    "noteCount": 342
  }
}
```

## 🎛️ 설정 옵션

### 난이도 레벨
- `easy`: 낮은 노트 밀도, 단순한 패턴
- `normal`: 보통 밀도, 기본 패턴
- `hard`: 높은 밀도, 복잡한 패턴
- `expert`: 매우 높은 밀도, 고급 패턴

### 지원 오디오 포맷
- WAV (기본값)
- MP3
- FLAC
- M4A

## 🔍 모니터링

### 헬스체크
```bash
# API Gateway 상태 확인
curl http://localhost:3000/api/health

# AI Service 상태 확인
curl http://localhost:8000/api/health
```

### 큐 상태 확인
```bash
# Redis 큐 상태
curl http://localhost:3000/api/queue/status
```

## 🚀 배포 (GCP Cloud Run)

### 1. GCP 설정
```bash
# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID

# 컨테이너 레지스트리 인증
gcloud auth configure-docker
```

### 2. 이미지 빌드 및 푸시
```bash
# API Gateway
docker build -t gcr.io/YOUR_PROJECT/rhythm-api ./api-gateway
docker push gcr.io/YOUR_PROJECT/rhythm-api

# AI Service
docker build -t gcr.io/YOUR_PROJECT/rhythm-ai -f ai-service/Dockerfile.gpu ./ai-service
docker push gcr.io/YOUR_PROJECT/rhythm-ai
```

### 3. Cloud Run 배포
```bash
# API Gateway 배포
gcloud run deploy rhythm-api \
  --image gcr.io/YOUR_PROJECT/rhythm-api \
  --region asia-northeast3 \
  --allow-unauthenticated

# AI Service 배포 (GPU 지원)
gcloud run deploy rhythm-ai \
  --image gcr.io/YOUR_PROJECT/rhythm-ai \
  --region asia-northeast3 \
  --gpu=1 \
  --gpu-type=nvidia-t4 \
  --memory=8Gi \
  --cpu=4
```

## 🧪 테스트

### 단위 테스트
```bash
# API Gateway 테스트
cd api-gateway
npm test

# AI Service 테스트
cd ai-service
pytest
```

### 통합 테스트
```bash
# 전체 시스템 테스트
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📊 성능 최적화

### GPU 메모리 최적화
- 배치 처리를 통한 GPU 활용률 향상
- 모델 캐싱으로 초기화 시간 단축
- 메모리 풀 사용으로 할당/해제 오버헤드 감소

### 큐 최적화
- 동일 URL 중복 처리 방지
- 우선순위 기반 작업 스케줄링
- 실패 작업 재시도 로직

## 🔐 보안 고려사항

### 저작권 준수
- 개인 사용 목적으로만 사용
- 원본 오디오 파일 처리 후 자동 삭제
- 비트맵 데이터만 저장

### 시스템 보안
- 입력 데이터 검증 및 제한
- 컨테이너 보안 설정
- 네트워크 격리

## 🛠️ 개발 환경 설정

### VS Code 설정
```json
{
  "python.defaultInterpreterPath": "./ai-service/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "eslint.workingDirectories": ["api-gateway"]
}
```

### 추천 확장 프로그램
- Python
- ES7+ React/Redux/React-Native snippets
- Docker
- REST Client

## 🤝 기여하기

1. Fork 프로젝트
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🙋‍♂️ 지원 및 문의

- 이슈 리포트: GitHub Issues
- 기술 문의: [이메일]
- 문서: [위키 페이지]

---

> 💡 **팁**: 개발 중 문제가 발생하면 `docker-compose logs` 명령어로 로그를 확인하세요!