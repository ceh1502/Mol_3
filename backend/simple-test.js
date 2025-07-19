const mongoose = require("mongoose");
  mongoose.connect("mongodb+srv://kenlee1502:John620620%40@minecraftcluster.eybdndl.mongodb.net/minecraft2d")
  .then(() => console.log("연결 성공"))
  .catch(err => console.error("연결 실패:", err));
