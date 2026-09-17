import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true, // sends the auth cookie with every request
});

export const checkUrlRequest = async (url) => {
    const response = await api.post("/api/check-url", { url });
    return response.data;
};

export const getHistoryRequest = async () => {
    const response = await api.get("/api/history");
    return response.data;
};

export default api;