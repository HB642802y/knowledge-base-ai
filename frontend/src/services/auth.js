import api from "./api";

const USER_STORAGE_KEY = "sdsi_user";

export function getLocalRole(user) {
  if (!user) return "collaborateur";
  if (user.role) return user.role;
  return user.email?.toLowerCase() === "admin@sdsi.com" ? "admin" : "collaborateur";
}

export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  const user = {
    id: data.id,
    email: data.email,
    full_name: data.full_name,
    role: data.role,
  };
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  return user;
}

export function logout() {
  localStorage.removeItem(USER_STORAGE_KEY);
}

export function getCurrentUser() {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(USER_STORAGE_KEY);
    return null;
  }
}

export function saveCurrentUser(user) {
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
}
