// 유튜브 메타데이터 추출 서비스
// yt-dlp를 통해 유튜브 비디오 정보를 가져옴
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

class YoutubeService {
  // 유튜브 비디오 메타데이터 추출
  async getVideoMetadata(url) {
    try {
      // yt-dlp를 사용하여 메타데이터 추출
      const command = `yt-dlp --dump-json --no-download "${url}"`;
      const { stdout } = await execAsync(command);
      
      const metadata = JSON.parse(stdout);
      
      return {
        id: metadata.id,
        title: metadata.title,
        uploader: metadata.uploader,
        duration: metadata.duration,
        thumbnail: metadata.thumbnail,
        description: metadata.description?.substring(0, 500) || '',
        uploadDate: metadata.upload_date,
        viewCount: metadata.view_count,
        likeCount: metadata.like_count,
        url: metadata.webpage_url,
        formats: this.extractAudioFormats(metadata.formats)
      };
    } catch (error) {
      console.error('YouTube metadata extraction error:', error);
      throw new Error('Failed to extract video metadata');
    }
  }

  // 오디오 포맷 정보 추출
  extractAudioFormats(formats) {
    return formats
      .filter(format => format.acodec !== 'none')
      .map(format => ({
        formatId: format.format_id,
        ext: format.ext,
        quality: format.quality,
        filesize: format.filesize,
        abr: format.abr // 오디오 비트레이트
      }))
      .sort((a, b) => (b.abr || 0) - (a.abr || 0))
      .slice(0, 3); // 상위 3개 포맷만 선택
  }

  // URL 유효성 검사
  validateUrl(url) {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
    return youtubeRegex.test(url);
  }

  // 비디오 가용성 확인
  async checkVideoAvailability(url) {
    try {
      const command = `yt-dlp --check-formats "${url}"`;
      await execAsync(command);
      return true;
    } catch (error) {
      return false;
    }
  }

  // 재생목록 처리
  async getPlaylistInfo(url) {
    try {
      const command = `yt-dlp --flat-playlist --dump-json "${url}"`;
      const { stdout } = await execAsync(command);
      
      const videos = stdout.trim().split('\n')
        .filter(line => line.trim())
        .map(line => JSON.parse(line));

      return {
        isPlaylist: true,
        videoCount: videos.length,
        videos: videos.map(video => ({
          id: video.id,
          title: video.title,
          duration: video.duration,
          url: `https://www.youtube.com/watch?v=${video.id}`
        }))
      };
    } catch (error) {
      console.error('Playlist processing error:', error);
      throw new Error('Failed to process playlist');
    }
  }
}

module.exports = new YoutubeService();