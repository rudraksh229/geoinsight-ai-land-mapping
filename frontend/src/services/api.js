import axios from "axios";

// Priority: Vercel Env Var -> Render Production URL -> Local Fallback
const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    "https://geoinsight-ai-land-mapping-backend.onrender.com",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
