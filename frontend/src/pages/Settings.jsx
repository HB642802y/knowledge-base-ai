import { useState } from "react";
import { getCurrentUser, saveCurrentUser } from "../services/auth";
import { updateProfile } from "../services/users";

export default function Settings() {
  const user = getCurrentUser();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");
    try {
      const updated = await updateProfile({
        id: user.id,
        email: user.email,
        full_name: fullName.trim(),
        current_password: newPassword ? currentPassword : undefined,
        new_password: newPassword || undefined,
      });
      saveCurrentUser({
        id: updated.id,
        email: updated.email,
        full_name: updated.full_name,
        role: updated.role,
      });
      setMessage("Profil mis à jour.");
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      setError(err.response?.data?.detail || "Échec de la mise à jour.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg">
      <h1 className="font-display text-2xl font-semibold text-slate-800">Paramètres</h1>
      <p className="mt-1 text-sm text-slate-500">
        Modifiez votre nom ou votre mot de passe.
      </p>

      <form onSubmit={handleSubmit} className="card-surface mt-6 space-y-4 p-6">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Email</label>
          <input className="input-field bg-slate-50" value={user?.email || ""} disabled />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Nom complet</label>
          <input
            className="input-field"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Mot de passe actuel (si changement)
          </label>
          <input
            type="password"
            className="input-field"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            Nouveau mot de passe
          </label>
          <input
            type="password"
            className="input-field"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            minLength={4}
          />
        </div>

        {message && (
          <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
            {message}
          </p>
        )}
        {error && (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </p>
        )}

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Enregistrement…" : "Enregistrer"}
        </button>
      </form>
    </div>
  );
}
