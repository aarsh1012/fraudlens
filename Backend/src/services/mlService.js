const axios = require("axios");

const getFraudPrediction = async (url) => {
    try {
        const response = await axios.post(`${process.env.ML_SERVICE_URL}/predict`, {
            url: url,
        });
        return response.data;
    } catch (error) {
        console.log("ML service call failed:", error.message);
        throw new Error("Failed to get prediction from ML service");
    }
};

module.exports = { getFraudPrediction };