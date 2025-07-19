const mongoose = require("mongoose");
  mongoose.connect("mongodb+srv://ken:ken0224@minecraftcluster.eybdndl.mongodb.net/minecraft2d")
  .then(() => console.log("연결 성공!"))
  .catch(err => console.error("연결 실패:", err));
