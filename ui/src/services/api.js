import axios from "axios";

// Create an Axios instance
const API = axios.create({
	baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:5050",
	timeout: process.env.NODE_ENV === "development" ? 10000 : 5000,
});

export { API };
