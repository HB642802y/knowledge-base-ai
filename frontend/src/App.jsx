import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";
import Navbar from "./components/Navbar";
import PrivateRoute from "./components/PrivateRoute";
import { getCurrentUser } from "./services/auth";
import Login from "./pages/Login";
import Chat from "./pages/Chat";
import Documents from "./pages/Documents";
import Upload from "./pages/Upload";
import Settings from "./pages/Settings";
import Admin from "./pages/Admin";
import Collaborator from "./pages/Collaborator";

function ApplicationLayout() {
  // Reading after each navigation keeps the layout in sync with login/logout,
  // while the user object remains deliberately stored in localStorage.
  const location = useLocation();
  const user = getCurrentUser();

  return (
    <div className="app-shell min-h-screen text-slate-100">
      <div className="app-ambient app-ambient-top" aria-hidden="true" />
      <div className="app-ambient app-ambient-bottom" aria-hidden="true" />
      <Navbar user={user} />
      <main
        key={location.pathname}
        className="relative mx-auto flex max-w-7xl gap-6 px-4 py-7 sm:px-6 lg:px-8"
      >
        <section className="min-w-0 flex-1">
          <Outlet />
        </section>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ApplicationLayout />}>
        <Route path="/" element={<Collaborator />} />
        <Route path="/collaborateur" element={<Collaborator />} />
        <Route path="/chat" element={<PrivateRoute><Chat /></PrivateRoute>} />
        <Route path="/documents" element={<PrivateRoute><Documents /></PrivateRoute>} />
        <Route path="/upload" element={<PrivateRoute><Upload /></PrivateRoute>} />
        <Route path="/settings" element={<PrivateRoute><Settings /></PrivateRoute>} />
        <Route
          path="/admin"
          element={
            <PrivateRoute requireAdmin>
              <Admin />
            </PrivateRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
