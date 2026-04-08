import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import HomePage from './pages/HomePage';
import HowItWorksPage from './pages/HowItWorksPage';
import KitsPage from './pages/KitsPage';
import KitDetailPage from './pages/KitDetailPage';
import RoleDetailPage from './pages/RoleDetailPage';
import LoginPage from './pages/LoginPage';
import ManagerDashboard from './pages/ManagerDashboard';
import CreateEditRolePage from './pages/CreateEditRolePage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              borderRadius: '8px',
              fontFamily: 'inherit',
              fontSize: '14px',
            },
          }}
        />
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="/kits" element={<KitsPage />} />
          <Route path="/kits/:id" element={<KitDetailPage />} />
          <Route path="/roles/:id" element={<RoleDetailPage />} />
          <Route path="/login" element={<LoginPage />} />

          {/* Manager routes (protected) */}
          <Route element={<ProtectedRoute />}>
            <Route path="/manager" element={<ManagerDashboard />} />
            <Route path="/manager/roles/new" element={<CreateEditRolePage />} />
            <Route path="/manager/roles/:id/edit" element={<CreateEditRolePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
