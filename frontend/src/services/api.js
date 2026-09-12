import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000"
});

export default API;

// Updation

const API_BASE_URL = "http://127.0.0.1:8000";

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("syncronalToken");

  const headers = {
    ...options.headers,
  };

  // Don't manually set Content-Type for FormData
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  let data;

  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.message ||
      "Something went wrong. Please try again.";

    throw new Error(
      typeof message === "string" ? message : JSON.stringify(message)
    );
  }

  return data;
}