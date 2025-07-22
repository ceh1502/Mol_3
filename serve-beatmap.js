const express = require('express');
const cors = require('cors');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 8001;

// CORS 설정
app.use(cors());

// JSON 파싱을 위한 미들웨어
app.use(express.json());

// JSON 파일을 정적으로 제공
app.use(express.static(path.join(__dirname, 'backend/audio_json')));

// 게임 파일들도 제공
app.use(express.static(__dirname));

// YouTube 처리 API
app.post('/process-youtube', async (req, res) => {
    try {
        const { url } = req.body;
        console.log(`🎵 YouTube URL 처리 시작: ${url}`);
        
        if (!url) {
            return res.status(400).json({ error: 'YouTube URL이 필요합니다' });
        }
        
        // YouTube URL 유효성 검사
        const youtubeRegex = /^https?:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+/;
        if (!youtubeRegex.test(url)) {
            return res.status(400).json({ error: '올바른 YouTube URL이 아닙니다' });
        }
        
        const gameId = uuidv4();
        const audioDir = path.join(__dirname, 'backend/audio_mp3');
        const jsonDir = path.join(__dirname, 'backend/audio_json');
        const audioFile = path.join(audioDir, `${gameId}.mp3`);
        const jsonFile = path.join(jsonDir, `${gameId}.json`);
        
        // 디렉토리 생성
        await fs.mkdir(audioDir, { recursive: true });
        await fs.mkdir(jsonDir, { recursive: true });
        
        console.log(`📥 음원 다운로드 시작...`);
        
        // yt-dlp로 음원 다운로드
        const ytDlpCommand = `yt-dlp -x --audio-format mp3 --audio-quality 0 -o "${audioFile.replace('.mp3', '.%(ext)s')}" "${url}"`;
        
        await new Promise((resolve, reject) => {
            exec(ytDlpCommand, { timeout: 120000 }, (error, stdout, stderr) => {
                if (error) {
                    console.error('yt-dlp 오류:', error);
                    reject(error);
                } else {
                    console.log('✅ 음원 다운로드 완료');
                    resolve();
                }
            });
        });
        
        console.log(`🎼 비트맵 생성 시작...`);
        
        // 간단한 비트맵 생성 (BPM 기반)
        const beatmap = await generateSimpleBeatmap(audioFile, gameId);
        
        // JSON 파일 저장
        await fs.writeFile(jsonFile, JSON.stringify(beatmap, null, 2));
        console.log('✅ 비트맵 생성 완료');
        
        // YouTube 제목 추출 (옵션)
        const videoTitle = await getYouTubeTitle(url);
        
        res.json({
            success: true,
            gameId: gameId,
            audioFile: `${gameId}.mp3`,
            beatmapFile: `${gameId}.json`,
            title: videoTitle || 'YouTube Music'
        });
        
    } catch (error) {
        console.error('YouTube 처리 오류:', error);
        res.status(500).json({ 
            error: '음원 처리 중 오류가 발생했습니다',
            details: error.message 
        });
    }
});

// YouTube 제목 추출 함수
async function getYouTubeTitle(url) {
    try {
        const command = `yt-dlp --get-title "${url}"`;
        return new Promise((resolve, reject) => {
            exec(command, { timeout: 30000 }, (error, stdout, stderr) => {
                if (error) {
                    console.warn('제목 추출 실패:', error.message);
                    resolve(null);
                } else {
                    resolve(stdout.trim());
                }
            });
        });
    } catch (error) {
        console.warn('제목 추출 중 오류:', error);
        return null;
    }
}

// 간단한 비트맵 생성 함수
async function generateSimpleBeatmap(audioFile, gameId) {
    // 오디오 길이 구하기
    const duration = await getAudioDuration(audioFile);
    
    // 기본 BPM (분석 없이 임시값)
    const bpm = 120;
    const beatInterval = 60 / bpm; // 초 단위
    
    const events = [];
    const lanes = 4;
    
    // 간단한 패턴 생성 (4초부터 시작해서 종료 5초 전까지)
    for (let time = 4; time < duration - 5; time += beatInterval) {
        // 랜덤한 레인에 노트 생성 (너무 조밀하지 않게)
        if (Math.random() < 0.6) { // 60% 확률로 노트 생성
            const lane = Math.floor(Math.random() * lanes);
            const noteType = Math.random() < 0.1 ? 'strong' : 'normal'; // 10% 확률로 strong
            
            events.push({
                time: parseFloat(time.toFixed(3)),
                lane: lane,
                type: noteType
            });
        }
    }
    
    // 시간 순으로 정렬
    events.sort((a, b) => a.time - b.time);
    
    return {
        tempo: bpm,
        lanes: lanes,
        duration: duration,
        events: events
    };
}

// 오디오 파일 길이 구하기
async function getAudioDuration(audioFile) {
    try {
        const command = `ffprobe -v quiet -show_entries format=duration -of csv="p=0" "${audioFile}"`;
        return new Promise((resolve, reject) => {
            exec(command, (error, stdout, stderr) => {
                if (error) {
                    console.warn('오디오 길이 추출 실패, 기본값 사용:', error.message);
                    resolve(180); // 기본 3분
                } else {
                    const duration = parseFloat(stdout.trim());
                    resolve(duration || 180);
                }
            });
        });
    } catch (error) {
        console.warn('오디오 길이 추출 중 오류:', error);
        return 180; // 기본 3분
    }
}

app.listen(PORT, () => {
    console.log(`🎵 Rhythm Game Server running on http://localhost:${PORT}`);
    console.log(`Beatmap available at: http://localhost:${PORT}/f0a648ba-8f39-4691-910f-aa10b8fdf042.json`);
});