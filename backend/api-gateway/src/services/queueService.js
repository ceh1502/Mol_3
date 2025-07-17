// Redis 큐 서비스
// Bull을 사용하여 작업 큐 관리 및 백그라운드 처리
const Queue = require('bull');
const Redis = require('ioredis');
const config = require('../config');

class QueueService {
  constructor() {
    // Redis 연결 설정
    this.redis = new Redis({
      host: config.REDIS_HOST || 'localhost',
      port: config.REDIS_PORT || 6379,
      password: config.REDIS_PASSWORD,
      db: config.REDIS_DB || 0
    });

    // 분석 작업 큐 생성
    this.analysisQueue = new Queue('audio analysis', {
      redis: {
        host: config.REDIS_HOST || 'localhost',
        port: config.REDIS_PORT || 6379,
        password: config.REDIS_PASSWORD,
        db: config.REDIS_DB || 0
      }
    });

    this.setupQueueEvents();
  }

  // 큐 이벤트 설정
  setupQueueEvents() {
    // 작업 완료 이벤트
    this.analysisQueue.on('completed', (job, result) => {
      console.log(`Job ${job.id} completed with result:`, result);
      this.notifyJobCompletion(job.id, result);
    });

    // 작업 실패 이벤트
    this.analysisQueue.on('failed', (job, error) => {
      console.error(`Job ${job.id} failed:`, error);
      this.notifyJobFailure(job.id, error);
    });

    // 작업 진행 이벤트
    this.analysisQueue.on('progress', (job, progress) => {
      console.log(`Job ${job.id} progress: ${progress}%`);
      this.updateJobProgress(job.id, progress);
    });
  }

  // 분석 작업 큐에 추가
  async addAnalysisJob(jobData) {
    try {
      const job = await this.analysisQueue.add('analyze-audio', jobData, {
        priority: this.getPriority(jobData.difficulty),
        delay: 0,
        attempts: 3,
        backoff: 'exponential',
        removeOnComplete: 10,
        removeOnFail: 5
      });

      // 작업 상태 Redis에 저장
      await this.redis.hset(`job:${job.id}`, {
        status: 'queued',
        createdAt: new Date().toISOString(),
        data: JSON.stringify(jobData)
      });

      return job.id;
    } catch (error) {
      console.error('Queue add error:', error);
      throw new Error('Failed to add job to queue');
    }
  }

  // 작업 우선순위 계산
  getPriority(difficulty) {
    const priorities = {
      easy: 3,
      normal: 2,
      hard: 1,
      expert: 0
    };
    return priorities[difficulty] || 2;
  }

  // 작업 상태 조회
  async getJobStatus(jobId) {
    try {
      const job = await this.analysisQueue.getJob(jobId);
      if (!job) {
        const cached = await this.redis.hgetall(`job:${jobId}`);
        return cached.status ? cached : null;
      }

      const state = await job.getState();
      const progress = job.progress();
      
      return {
        id: jobId,
        status: state,
        progress,
        data: job.data,
        createdAt: job.timestamp,
        processedAt: job.processedOn,
        finishedAt: job.finishedOn,
        failedReason: job.failedReason
      };
    } catch (error) {
      console.error('Job status error:', error);
      return null;
    }
  }

  // 작업 진행 상태 업데이트
  async updateJobProgress(jobId, progress) {
    try {
      await this.redis.hset(`job:${jobId}`, {
        progress,
        updatedAt: new Date().toISOString()
      });
    } catch (error) {
      console.error('Progress update error:', error);
    }
  }

  // 작업 완료 알림
  async notifyJobCompletion(jobId, result) {
    try {
      await this.redis.hset(`job:${jobId}`, {
        status: 'completed',
        result: JSON.stringify(result),
        completedAt: new Date().toISOString()
      });

      // WebSocket을 통한 실시간 알림 (추후 구현)
      // this.webSocketService.notify(jobId, 'completed', result);
    } catch (error) {
      console.error('Job completion notification error:', error);
    }
  }

  // 작업 실패 알림
  async notifyJobFailure(jobId, error) {
    try {
      await this.redis.hset(`job:${jobId}`, {
        status: 'failed',
        error: error.message,
        failedAt: new Date().toISOString()
      });

      // WebSocket을 통한 실시간 알림 (추후 구현)
      // this.webSocketService.notify(jobId, 'failed', { error: error.message });
    } catch (error) {
      console.error('Job failure notification error:', error);
    }
  }

  // 작업 취소
  async cancelJob(jobId) {
    try {
      const job = await this.analysisQueue.getJob(jobId);
      if (job) {
        await job.remove();
        await this.redis.hset(`job:${jobId}`, {
          status: 'cancelled',
          cancelledAt: new Date().toISOString()
        });
        return true;
      }
      return false;
    } catch (error) {
      console.error('Job cancellation error:', error);
      throw new Error('Failed to cancel job');
    }
  }

  // 큐 상태 조회
  async getQueueStats() {
    try {
      const waiting = await this.analysisQueue.getWaiting();
      const active = await this.analysisQueue.getActive();
      const completed = await this.analysisQueue.getCompleted();
      const failed = await this.analysisQueue.getFailed();

      return {
        waiting: waiting.length,
        active: active.length,
        completed: completed.length,
        failed: failed.length
      };
    } catch (error) {
      console.error('Queue stats error:', error);
      return null;
    }
  }
}

module.exports = new QueueService();