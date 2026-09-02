import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001/api/v1";

const api = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  if (Object.prototype.hasOwnProperty.call(config.headers || {}, "X-User-Email")) {
    if (!config.headers["X-User-Email"]) {
      delete config.headers["X-User-Email"];
    }
    return config;
  }

  try {
    const user = JSON.parse(localStorage.getItem("sdsi_user") || "null");
    if (user?.email) {
      config.headers["X-User-Email"] = user.email;
    }
  } catch {
    // An invalid local value is handled by the authentication guard.
  }
  return config;
});

export default api;
