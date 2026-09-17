const express = require("express");
const router = express.Router();
const { checkUrl, getHistory } = require("../controllers/urlCheck.controller");
const protect = require("../middlewares/auth.middleware");

router.post("/check-url", protect, checkUrl);
router.get("/history", protect, getHistory);

module.exports = router;