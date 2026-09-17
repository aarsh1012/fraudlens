const UrlCheck = require("../models/urlCheck.model");
const { getFraudPrediction } = require("../services/mlService");

const checkUrl = async (req, res) => {
    try {
        const { url } = req.body;

        if (!url) {
            return res.status(400).json({ message: "URL is required" });
        }

        const result = await getFraudPrediction(url);

        const savedCheck = await UrlCheck.create({
            user: req.userId,
            url: result.url,
            prediction: result.prediction,
            confidence: result.confidence,
            note: result.note || null,
        });

        res.status(200).json(savedCheck);
    } catch (error) {
        console.log(error);
        res.status(500).json({ message: "URL check failed" });
    }
};

const getHistory = async (req, res) => {
    try {
        const history = await UrlCheck.find({ user: req.userId }).sort({ createdAt: -1 });
        res.status(200).json({ history });
    } catch (error) {
        console.log(error);
        res.status(500).json({ message: "Failed to fetch history" });
    }
};

module.exports = { checkUrl, getHistory };