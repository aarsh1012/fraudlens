const express = require("express");
const router = express.Router();
const { registerUser, loginUser, logoutUser, getMe } = require("../controllers/auth.controller");
const protect = require("../middlewares/auth.middleware");

router.post("/register", registerUser);
router.post("/login", loginUser);
router.post("/logout", logoutUser);
router.get("/get-me", protect, getMe);

module.exports = router;