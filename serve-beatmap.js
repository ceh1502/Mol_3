/** -----------------------------------------------------------------
 *  Rhythm-Game 프론트 프록시 서버 (포트 8001)
 *  · /process-youtube  → FastAPI 8000 호출해 mp3·비트맵 생성
 *  · /audio/*, /beatmaps/*          정적 파일 서빙
 *  · ./ (index.html · JS · CSS)      프론트 소스 서빙
 * -----------------------------------------------------------------*/

const express = require("express");
const cors = require("cors");
const path = require("path");
// Node v18+ 는 fetch가 내장.  v16 이하면 ↓ 주석 해제 후 사용
// const fetch   = (...a) => import("node-fetch").then(({default:f}) => f(...a));

const app = express();
const PORT = 8001;

// FastAPI 8000 엔드포인트
const BACKEND_API = "http://localhost:8000/api/audio/generate";

/* ---------- 공통 미들웨어 ---------- */
app.use(cors());
app.use(express.json());

/* ---------- 정적 파일 매핑 ----------
 * FastAPI 가 실제로 파일을 저장하는 경로(/tmp/...)와 같아야 합니다.
 */
app.use("/audio", express.static("backend/audio_mp3"));
app.use("/beatmaps", express.static("backend/audio_json"));

/* ---------- 프론트(asset) 서빙 ---------- */
app.use(express.static(__dirname));

/* ---------- POST /process-youtube ---------- */
app.post("/process-youtube", async (req, res) => {
  try {
    const { url } = req.body;
    if (!url)
      return res.status(400).json({ error: "YouTube URL이 필요합니다" });

    const ytRegex =
      /^https?:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+/;
    if (!ytRegex.test(url))
      return res.status(400).json({ error: "올바른 YouTube URL이 아닙니다" });

    /* 1) FastAPI로 프록시 요청 */
    const apiRes = await fetch(
      `${BACKEND_API}?url=${encodeURIComponent(url)}`,
      { method: "POST" }
    );
    if (!apiRes.ok) {
      console.error("[FastAPI] 응답 오류:", await apiRes.text());
      return res.status(502).json({ error: "FastAPI 처리 실패" });
    }

    /* 2) FastAPI 응답 → 프론트용으로 가공 */
    const { beatmap_id, mp3_path, title } = await apiRes.json();

    const mp3File = path.basename(mp3_path); // xrMk87j81wk.mp3
    const mp3_url = `/audio/${mp3File}`;
    const beatmap_url = `/beatmaps/${beatmap_id}`; // .json 포함

    /* 3) 프론트로 반환 */
    res.json({
      success: true,
      mp3_url,
      beatmap_url,
      title,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "서버 내부 오류", details: err.message });
  }
});

/* ---------- 서버 시작 ---------- */
app.listen(PORT, () =>
  console.log(`🎵 Front-proxy server running → http://localhost:${PORT}`)
);
