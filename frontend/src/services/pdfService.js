import api from "./api";

export const generatePDF = (data) => {
    return api.post("/pdf/generate", data, {
        responseType: "blob",
    });
};
