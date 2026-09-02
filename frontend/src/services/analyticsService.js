import api from "./api";

export const getAnalytics = () => {
    return api.get("/analytics/summary");
};
