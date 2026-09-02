import api from "./api";

export const getDashboardStats = async () => {
    const response = await api.get("/dashboard/stats");
    return response.data;
};

export const getDashboardCharts = async () => {
    const response = await api.get("/dashboard/charts");
    return response.data;
};

export const getRecentReports = async () => {
    const response = await api.get("/reports");
    return response.data;
};

export const createAnalysis = async (data) => {
    const response = await api.post("/reports", data);
    return response.data;
};
