// src/utils/api.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/",
  withCredentials: true,  // This is crucial for sending cookies
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add request interceptor to include token from localStorage

//Use for wishlist .. remove for register, checking what to do
// api.interceptors.request.use(
//   (config) => {
//     const token = localStorage.getItem('authToken');
//     if (token) {
//       config.headers.Authorization = `Bearer ${token}`;
//     }
//     return config;
//   },
//   (error) => {
//     return Promise.reject(error);
//   }
// );

export default api;