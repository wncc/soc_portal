import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

/**
 * Hook to prevent back button navigation to authenticated pages after logout
 * This ensures users can't press back button to access protected content
 */
export const usePreventBackAfterLogout = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const authToken = localStorage.getItem('authToken');
    
    // Protected routes that require authentication
    const protectedPaths = [
      '/current_projects',
      '/wishlist',
      '/PreferenceForm',
      '/PreferenceFormFilled',
      '/mentor/home',
      '/mentor/add-project',
      '/mentor/edit-project',
      '/manager',
    ];
    
    // Check if current path is protected (including domain-scoped routes)
    const isProtectedRoute = protectedPaths.some(path => 
      location.pathname.includes(path)
    );
    
    // If on protected route without auth token, redirect to login
    if (isProtectedRoute && !authToken) {
      console.log('[BACK GUARD] Prevented back navigation to protected route');
      navigate('/login', { replace: true });
    }
  }, [location, navigate]);
};

/**
 * Component to add to App.js to prevent back button after logout
 */
export const BackButtonGuard = () => {
  usePreventBackAfterLogout();
  return null;
};
