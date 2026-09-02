import api from "./api";

export const login = (credentials) => {
    return api.post("/auth/login", {
        email: credentials.email,
        password: credentials.password,
    });
};

export const register = (user) => {
    return api.post("/auth/register", user);
};

export const getCurrentUser = () => {
    return api.get("/auth/me");
};