import api from "./api";

export const analyzeLand = (data) => {
    return api.post("/mapping/analyze", data);
};
