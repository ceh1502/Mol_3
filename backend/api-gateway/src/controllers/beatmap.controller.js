// 비트맵 조회 및 다운로드 컨트롤러
// 완성된 비트맵을 프론트엔드에 제공하는 역할
const beatmapService = require('../services/beatmapService');
const storageService = require('../services/storageService');

class BeatmapController {
  // 비트맵 조회 (JSON 형태)
  async getBeatmap(req, res) {
    try {
      const { jobId } = req.params;
      
      // 작업 완료 상태 확인
      const job = await beatmapService.getJobResult(jobId);
      
      if (!job) {
        return res.status(404).json({ error: 'Beatmap not found' });
      }

      if (job.status === 'processing') {
        return res.json({
          status: 'processing',
          progress: job.progress || 0,
          estimatedTime: job.estimatedTime
        });
      }

      if (job.status === 'failed') {
        return res.status(500).json({
          status: 'failed',
          error: job.error || 'Processing failed'
        });
      }

      // 완성된 비트맵 반환
      res.json({
        status: 'completed',
        beatmap: job.beatmap,
        metadata: job.metadata,
        downloadUrl: job.downloadUrl,
        createdAt: job.createdAt
      });

    } catch (error) {
      console.error('Beatmap retrieval error:', error);
      res.status(500).json({ error: 'Failed to retrieve beatmap' });
    }
  }

  // 비트맵 파일 다운로드
  async downloadBeatmap(req, res) {
    try {
      const { jobId } = req.params;
      const { format = 'json' } = req.query;

      // 저장소에서 비트맵 파일 가져오기
      const fileStream = await storageService.downloadBeatmapFile(jobId, format);
      
      if (!fileStream) {
        return res.status(404).json({ error: 'Beatmap file not found' });
      }

      // 파일 다운로드 헤더 설정
      res.setHeader('Content-Type', 'application/octet-stream');
      res.setHeader('Content-Disposition', `attachment; filename="beatmap_${jobId}.${format}"`);
      
      fileStream.pipe(res);

    } catch (error) {
      console.error('Beatmap download error:', error);
      res.status(500).json({ error: 'Failed to download beatmap' });
    }
  }

  // 사용자의 비트맵 목록 조회
  async getBeatmapList(req, res) {
    try {
      const { userId } = req.params;
      const { page = 1, limit = 10 } = req.query;

      const beatmaps = await beatmapService.getUserBeatmaps(userId, {
        page: parseInt(page),
        limit: parseInt(limit)
      });

      res.json({
        beatmaps,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total: beatmaps.length
        }
      });

    } catch (error) {
      console.error('Beatmap list error:', error);
      res.status(500).json({ error: 'Failed to retrieve beatmap list' });
    }
  }
}

module.exports = new BeatmapController();