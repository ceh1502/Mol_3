// AI 서비스 통신 클래스
// Python FastAPI AI 서비스와 통신하여 오디오 분석 및 비트맵 생성 요청
const axios = require('axios');
const config = require('../config');

class AiService {
  constructor() {
    this.aiServiceUrl = config.AI_SERVICE_URL || 'http://ai-service:8000';
    this.client = axios.create({
      baseURL: this.aiServiceUrl,
      timeout: 300000, // 5분 타임아웃
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  // 오디오 분석 요청
  async analyzeAudio(audioData) {
    try {
      const response = await this.client.post('/analyze', {
        audioPath: audioData.path,
        metadata: audioData.metadata,
        difficulty: audioData.difficulty
      });

      return response.data;
    } catch (error) {
      console.error('AI audio analysis error:', error);
      throw new Error('Failed to analyze audio');
    }
  }

  // 비트맵 생성 요청
  async generateBeatmap(analysisResult, difficulty = 'normal') {
    try {
      const response = await this.client.post('/generate-beatmap', {
        analysis: analysisResult,
        difficulty,
        gameMode: 'rhythm'
      });

      return response.data;
    } catch (error) {
      console.error('Beatmap generation error:', error);
      throw new Error('Failed to generate beatmap');
    }
  }

  // 전체 파이프라인 실행 (오디오 분석 + 비트맵 생성)
  async processFullPipeline(youtubeUrl, difficulty = 'normal') {
    try {
      const response = await this.client.post('/process-pipeline', {
        youtubeUrl,
        difficulty,
        options: {
          audioFormat: 'wav',
          sampleRate: 44100,
          channels: 2
        }
      });

      return response.data;
    } catch (error) {
      console.error('Full pipeline processing error:', error);
      throw new Error('Failed to process full pipeline');
    }
  }

  // AI 서비스 상태 확인
  async getServiceStatus() {
    try {
      const response = await this.client.get('/health');
      return {
        status: 'healthy',
        version: response.data.version,
        gpuStatus: response.data.gpu_status,
        modelStatus: response.data.model_status
      };
    } catch (error) {
      console.error('AI service status error:', error);
      return {
        status: 'unhealthy',
        error: error.message
      };
    }
  }

  // 작업 진행 상태 확인
  async getJobProgress(jobId) {
    try {
      const response = await this.client.get(`/job-status/${jobId}`);
      return response.data;
    } catch (error) {
      console.error('Job progress error:', error);
      throw new Error('Failed to get job progress');
    }
  }

  // 작업 취소
  async cancelJob(jobId) {
    try {
      const response = await this.client.delete(`/job/${jobId}`);
      return response.data;
    } catch (error) {
      console.error('Job cancellation error:', error);
      throw new Error('Failed to cancel job');
    }
  }
}

module.exports = new AiService();