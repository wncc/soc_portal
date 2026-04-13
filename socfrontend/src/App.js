import './App.css';
import React, { useEffect, useState } from 'react';

import UnifiedNavbar from './components/UnifiedNavbar';
import Login from './mentee/pages/Login';
import Projects from './mentee/pages/Projects';
import './mentee/components/scrollable.css';
import PhoneNumberModal from './components/PhoneNumberModal';
import { BackButtonGuard } from './hooks/usePreventBackAfterLogout';

import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';

import ProjectDetails from './mentee/pages/ProjectDetails';
import PreferenceForm from './mentee/pages/PreferenceForm';
import ProtectedRoutes from './mentee/components/ProtectedRoutes';
import LoginRoute from './mentee/components/LoginRoute';
import PreferenceFormFilled from './mentee/pages/PreferenceFormFilled';
import api from './utils/api';
import Wishlist from './mentee/pages/Wishlist';
import Home from './mentee/pages/Home';
import LandingPage from './mentor/LandingPage';
import Form from './mentor/Form';
import URLGuard from './URLGuard';
import Loading from './mentee/pages/Loading';
import NoPage from './mentee/components/NoPage';
import EditProject from './mentor/EditProject';
import Admin from './mentee/pages/Admin';

// New multi-domain imports
import SummerOfTech from './home/SummerOfTech';
import ManagerDashboard from './manager/ManagerDashboard';
import BecomeManager from './manager/BecomeManager';
import DebugMemberships from './components/DebugMemberships';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

// ProtectedRoute for manager-only routes
function ManagerRoute({ children }) {
  const [checking, setChecking] = useState(true);
  const [isManager, setIsManager] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const checkManager = async () => {
      const managerFlag = localStorage.getItem('is_manager') === 'true';
      if (!managerFlag) {
        // Double check with API
        try {
          const res = await api.get(`${BACKEND}/accounts/my-memberships/`);
          const actuallyManager = res.data.is_manager || false;
          localStorage.setItem('is_manager', actuallyManager ? 'true' : 'false');
          setIsManager(actuallyManager);
        } catch (e) {
          setIsManager(false);
        }
      } else {
        setIsManager(true);
      }
      setChecking(false);
    };
    checkManager();
  }, []);

  if (checking) {
    return (
      <div className="h-screen flex justify-center items-center">
        <div className="flex gap-2">
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
        </div>
      </div>
    );
  }

  if (!isManager) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  const [authToken, setAuthToken] = useState(localStorage.getItem('authToken'));
  const [isManager, setIsManager] = useState(localStorage.getItem('is_manager') === 'true');
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [needsPhoneUpdate, setNeedsPhoneUpdate] = useState(false);
  const role = localStorage.getItem('role');
  const location = useLocation();

  // Listen for storage changes (when Loading.jsx sets authToken)
  useEffect(() => {
    const handleStorageChange = () => {
      setAuthToken(localStorage.getItem('authToken'));
      setIsManager(localStorage.getItem('is_manager') === 'true');
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  useEffect(() => {
    setIsCheckingAuth(true);
    api
      .get(`${BACKEND}/accounts/isloggedin/`)
      .then((res) => {
        const loggedIn = res.data.status === 'YES';
        if (!loggedIn) {
          // Clear invalid tokens
          localStorage.removeItem('authToken');
          localStorage.removeItem('is_manager');
          localStorage.removeItem('memberships');
          setAuthToken(null);
          setIsManager(false);
        } else {
          setAuthToken(localStorage.getItem('authToken'));
          // Refresh memberships on each load
          api.get(`${BACKEND}/accounts/my-memberships/`).then((r) => {
            const manager = r.data.is_manager || false;
            setIsManager(manager);
            localStorage.setItem('is_manager', manager ? 'true' : 'false');
            if (r.data.memberships) {
              localStorage.setItem('memberships', JSON.stringify(r.data.memberships));
            }
            // Check if phone number update is needed
            setNeedsPhoneUpdate(r.data.needs_phone_update || false);
          }).catch(() => {});
        }
        setIsCheckingAuth(false);
      })
      .catch((error) => {
        // On error (including 401 for invalid token), clear everything
        console.log('[APP] isloggedin check failed:', error.response?.status);
        localStorage.removeItem('authToken');
        localStorage.removeItem('is_manager');
        localStorage.removeItem('memberships');
        setAuthToken(null);
        setIsManager(false);
        setIsCheckingAuth(false);
      });
  }, [location]);

  if (isCheckingAuth) {
    return (
      <div className="h-screen flex justify-center items-center">
        <div className="flex gap-2">
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
          <div className="w-5 h-5 rounded-full animate-pulse bg-blue-600" />
        </div>
      </div>
    );
  }

  // Hide navbar only on become-manager and loading pages
  const hideNavbar = location.pathname.startsWith('/become-manager') || location.pathname === '/loading';

  return (
    <>
      <div className="background">
        <URLGuard />
        <BackButtonGuard />
        {!hideNavbar && <UnifiedNavbar />}
        {needsPhoneUpdate && authToken && (
          <PhoneNumberModal onClose={() => setNeedsPhoneUpdate(false)} />
        )}
        <Routes>
          {/* ============================================================
              Public / Home
          ============================================================ */}
          <Route
            path="/"
            element={<SummerOfTech authToken={authToken} />}
          />

          {/* ============================================================
              Manager Bootstrap URL
              /become-manager/:secret — visited by ITC managers to gain access
          ============================================================ */}
          <Route path="/become-manager/:secret" element={<BecomeManager />} />

          {/* ============================================================
              Debug Route - Remove in production
          ============================================================ */}
          <Route path="/debug-memberships" element={<DebugMemberships />} />

          {/* ============================================================
              Manager Dashboard (manager role required)
          ============================================================ */}
          <Route
            path="/manager"
            element={
              <ManagerRoute>
                <ManagerDashboard />
              </ManagerRoute>
            }
          />

          {/* ============================================================
              Unauthenticated routes
          ============================================================ */}
          <Route element={<LoginRoute authToken={authToken} />}>
            <Route path="/login" element={<Login />} />
            <Route path="/p23logad" element={<Admin />} />
            <Route path="/loading" element={<Loading />} />
          </Route>

          {/* ============================================================
              Legacy SOC routes (backward compatible)
              These still work so existing bookmarks/links don't break.
          ============================================================ */}
          <Route element={<ProtectedRoutes authToken={authToken} />}>
            <Route path="/current_projects" element={<Projects />} />
            <Route path="/current_projects/:ProjectId" element={<ProjectDetails />} />
            <Route path="/wishlist" element={<Wishlist />} />
            <Route path="/PreferenceForm" element={<PreferenceForm />} />
            <Route path="/PreferenceFormFilled" element={<PreferenceFormFilled />} />
            <Route path="/mentor/add-project" element={<Form />} />
            <Route path="/mentor/edit-project" element={<EditProject />} />
            <Route path="/mentor/home" element={<LandingPage />} />
          </Route>

          {/* ============================================================
              Domain-scoped routes: /:domain/...
              e.g. /soc/current_projects, /soq/mentor/home
          ============================================================ */}
          <Route element={<ProtectedRoutes authToken={authToken} />}>
            {/* Mentee portal */}
            <Route path="/:domain/current_projects" element={<Projects />} />
            <Route path="/:domain/current_projects/:ProjectId" element={<ProjectDetails />} />
            <Route path="/:domain/wishlist" element={<Wishlist />} />
            <Route path="/:domain/PreferenceForm" element={<PreferenceForm />} />
            <Route path="/:domain/PreferenceFormFilled" element={<PreferenceFormFilled />} />

            {/* Mentor portal */}
            <Route path="/:domain/mentor/home" element={<LandingPage />} />
            <Route path="/:domain/mentor/add-project" element={<Form />} />
            <Route path="/:domain/mentor/edit-project" element={<EditProject />} />
          </Route>

          <Route path="*" element={<NoPage />} />
        </Routes>
      </div>
    </>
  );
}
