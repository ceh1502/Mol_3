const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 8001;

// CORS 설정
app.use(cors());

// JSON 파일을 정적으로 제공
app.use(express.static(path.join(__dirname, 'backend/audio_json')));

// 게임 파일들도 제공
app.use(express.static(__dirname));

app.listen(PORT, () => {
    console.log(`🎵 Rhythm Game Server running on http://localhost:${PORT}`);
    console.log(`Beatmap available at: http://localhost:${PORT}/f0a648ba-8f39-4691-910f-aa10b8fdf042.json`);
});