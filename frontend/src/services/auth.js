import api from "./api";

const USER_STORAGE_KEY = "sdsi_user";

/**
 * TEMPORAIRE — à supprimer quand le backend exposera un vrai rôle
 * (table roles branchée aux users / JWT claims).
 *
 * Aujourd'hui le backend ne renvoie que { id, email, full_name }.
 * On dérive donc un rôle purement local pour piloter la navigation UI.
 */
export function getLocalRole(email) {
  if (!email) return "collaborateur";
  return email.toLowerCase() === "admin@sdsi.com" ? "admin" : "collaborateur";
}

export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  // Pas de JWT : on stocke uniquement l'objet user renvoyé par le stub auth.
  const user = {
    id: data.id,
    email: data.email,
    full_name: data.full_name,
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
