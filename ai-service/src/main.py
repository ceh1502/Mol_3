# FastAPI 메인 애플리케이션
# GPU 기반 오디오 분석 및 비트맵 생성을 위한 AI 서비스
import os
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# 로컬 모듈 임포트
from api.analyze import router as analyze_router
from api.beatmap import router as beatmap_router
from api.health import router as health_router
from utils.gpu_manager import GPUManager
from utils.model_loader import ModelLoader

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Rhythm Game AI Service",
    description="GPU 기반 오디오 분석 및 비트맵 생성 서비스",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 글로벌 변수
gpu_manager = None
model_loader = None

@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 GPU 및 모델 초기화"""
    global gpu_manager, model_loader
    
    try:
        # GPU 매니저 초기화
        gpu_manager = GPUManager()
        gpu_status = gpu_manager.get_gpu_status()
        
        if gpu_status['available']:
            logger.info(f"GPU 사용 가능: {gpu_status['name']}")
        else:
            logger.warning("GPU 사용 불가 - CPU 모드로 실행")
        
        # 모델 로더 초기화
        model_loader = ModelLoader()
        await model_loader.load_models()
        
        logger.info("AI 서비스 시작 완료")
        
    except Exception as e:
        logger.error(f"서비스 시작 중 오류: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """서비스 종료 시 정리 작업"""
    try:
        if model_loader:
            await model_loader.cleanup()
        if gpu_manager:
            gpu_manager.cleanup()
        logger.info("AI 서비스 종료 완료")
    except Exception as e:
        logger.error(f"서비스 종료 중 오류: {e}")

# 라우터 등록
app.include_router(analyze_router, prefix="/api/analyze", tags=["분석"])
app.include_router(beatmap_router, prefix="/api/beatmap", tags=["비트맵"])
app.include_router(health_router, prefix="/api/health", tags=["헬스체크"])

# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리기"""
    logger.error(f"예외 발생: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "내부 서버 오류가 발생했습니다."}
    )

# 루트 엔드포인트
@app.get("/")
async def root():
    """서비스 정보 반환"""
    return {
        "name": "Rhythm Game AI Service",
        "version": "1.0.0",
        "status": "running",
        "gpu_available": gpu_manager.get_gpu_status()['available'] if gpu_manager else False
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        workers=1,  # GPU 사용 시 단일 워커 권장
        log_level="info"
    )