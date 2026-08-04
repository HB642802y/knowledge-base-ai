import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import PrivateRoute from "./components/PrivateRoute";
import Sidebar from "./components/Sidebar";
import Admin from "./pages/Admin";
import Chat from "./pages/Chat";
import Documents from "./pages/Documents";
import Login from "./pages/Login";
import Upload from "./pages/Upload";
import { getCurrentUser, getLocalRole } from "./services/auth";

function AppLayout({ children }) {
  const user = getCurrentUser();
  const role = getLocalRole(user?.email);

  return (
    <div className="min-h-screen">
      <Navbar user={user} role={role} />
      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <Sidebar role={role} />
        <main className="min-w-0 flex-1">{children}</main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route
        path="/chat"
        element={
          <PrivateRoute>
            <AppLayout>
              <Chat />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/documents"
        element={
          <PrivateRoute>
            <AppLayout>
              <Documents />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/upload"
        element={
          <PrivateRoute>
            <AppLayout>
              <Upload />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <PrivateRoute requireAdmin>
            <AppLayout>
              <Admin />
            </AppLayout>
          </PrivateRoute>
        }
      />

      <Route path="/" element={<Navigate to="/chat" replace />} />
      <Route path="*" element={<Navigate to="/chat" replace />} />
    </Routes>
  );
}
