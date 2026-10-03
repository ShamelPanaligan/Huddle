// Responsible for talking to FastAPI backend. Handles token storage and retrieval, and automatically adds the token to requests.
const BASE_URL = "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

async function apiFetch(path, options = {}) {
  const token = getToken();

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new Error(errorBody.detail || "Request failed");
  }

  return response.json();
}

export async function login(email, password) {
  const data = await apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({
      email: email,
      password: password
    })
  })
  setToken(data.access_token);
  return data;
}

export async function register(email, password) {
  const data = await apiFetch("/auth/register",{
    method: "POST",
    body: JSON.stringify({
      email:email,
      password:password
    })
  })
  return data;
}

export async function listEventIdeas() {
  const data = await apiFetch("/event-ideas");
  return data;
}

export async function createEventIdea(idea) {
  const data = await apiFetch("/event-ideas",{
    method: "POST",
    body: JSON.stringify(idea)
  })
  return data;
}