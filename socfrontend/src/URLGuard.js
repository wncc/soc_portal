import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function URLGuard() {
  const navigate = useNavigate();
  const location = useLocation();
  const role = localStorage.getItem('role');

  useEffect(() => {
    if (!role) return; // Avoid unnecessary redirections before role is loaded

    // const mentorRoutes = ['/mentor/home', '/mentor/add-project','/mentor/edit-project'];
    const mentorRoutes = ['/mentor/home'];
    // const menteeRoutes = ['/PreferenceFormFilled','/current_projects', '/wishlist', '/PreferenceForm'];
    const menteeRoutes = [];
    // const authRoutes = ["/login", "/register", "/registerSuccess", "/verify-email"];
    const authRoutes = ['/login',"/p23logad"];

    const normalizedPath = location.pathname.replace(/\/+$/, '');
    const isProjectDetailsRoute = /^\/current_projects\/[^/]+$/.test(location.pathname);

    if (role === 'mentee' && mentorRoutes.includes(normalizedPath)) {
      navigate('/', { replace: true });
    } else if (role === 'mentor' && (menteeRoutes.includes(normalizedPath) || isProjectDetailsRoute)) {
      navigate('/mentor/home', { replace: true });
    } else if (
      !mentorRoutes.includes(normalizedPath) &&
      !menteeRoutes.includes(normalizedPath) &&
      !authRoutes.includes(normalizedPath) &&
      !isProjectDetailsRoute
    ) {
      navigate('/', { replace: true });
    }
  }, [location.pathname, role, navigate]);

  return null;
}
