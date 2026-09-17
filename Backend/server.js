require("dotenv").config();
const express = require("express");
const cors = require("cors");
const cookieParser = require("cookie-parser");
const connectToDB = require("./src/config/database");
const authRoutes = require("./src/routes/auth.routes");
const urlCheckRoutes = require("./src/routes/urlCheck.routes");

const app = express();

connectToDB();

app.use(express.json());
app.use(cookieParser());
app.use(cors({
    origin: process.env.FRONTEND_URL,
    credentials: true,
}));

app.use("/api/auth", authRoutes);
app.use("/api", urlCheckRoutes);


app.get("/", (req, res) => {
    res.send("FraudLens backend is running");
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on ${PORT}`);
});