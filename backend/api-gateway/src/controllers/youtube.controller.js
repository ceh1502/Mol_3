// 유튜브 URL 처리 컨트롤러
// 유튜브 링크를 받아 메타데이터 추출 및 비트맵 생성 작업 큐에 추가
const youtubeService = require('../services/youtubeService');
const aiService = require('../services/aiService');
const queueService = require('../services/queueService');
const { validateYoutubeUrl } = require('../utils/validation');

class YoutubeController {
  // 유튜브 URL 분석 요청 처리
  async analyzeUrl(req, res) {
    try {
      const { url, difficulty = 'normal' } = req.body;

      // URL 유효성 검사
      if (!validateYoutubeUrl(url)) {
        return res.status(400).json({ error: 'Invalid YouTube URL' });
      }

      // 유튜브 메타데이터 추출 (제목, 길이, 썸네일 등)
      const metadata = await youtubeService.getVideoMetadata(url);
      
      // 비디오 길이 제한 (10분 이하)
      if (metadata.duration > 600) {
        return res.status(400).json({ error: 'Video too long (max 10 minutes)' });
      }

      // 작업 큐에 추가
      const jobId = await queueService.addAnalysisJob({
        url,
        difficulty,
        metadata
      });

      res.json({
        jobId,
        status: 'queued',
        metadata,
        estimatedTime: Math.ceil(metadata.duration / 4) // 대략적인 처리 시간
      });

    } catch (error) {
      console.error('YouTube analysis error:', error);
      res.status(500).json({ error: 'Failed to process YouTube URL' });
    }
  }

  // 작업 상태 확인
  async getJobStatus(req, res) {
    try {
      const { jobId } = req.params;
      const status = await queueService.getJobStatus(jobId);
      
      if (!status) {
        return res.status(404).json({ error: 'Job not found' });
      }

      res.json(status);
    } catch (error) {
      console.error('Job status error:', error);
      res.status(500).json({ error: 'Failed to get job status' });
    }
  }
}

module.exports = new YoutubeController();