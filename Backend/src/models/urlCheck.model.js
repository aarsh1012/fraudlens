const mongoose = require("mongoose");

const urlCheckSchema = new mongoose.Schema({
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "User",
        required: true,
    },
    url: {
        type: String,
        required: true,
    },
    prediction: {
        type: String,
        enum: ["LEGITIMATE", "PHISHING"],
        required: true,
    },
    confidence: {
        type: Number,
        required: true,
    },
    note: {
        type: String,
        default: null,
    },
}, { timestamps: true });

module.exports = mongoose.model("UrlCheck", urlCheckSchema);