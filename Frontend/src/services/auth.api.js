import api from "./urlCheck.api";

export const register = async ({ fullName, email, password }) => {
    const response = await api.post("/api/auth/register", { fullName, email, password });
    return response.data;
};

export const Login = async ({ email, password }) => {
    const response = await api.post("/api/auth/login", { email, password });
    return response.data;
};

export const logout = async () => {
    const response = await api.post("/api/auth/logout");
    return response.data;
};

export const getMe = async () => {
    const response = await api.get("/api/auth/get-me");
    return response.data;
};