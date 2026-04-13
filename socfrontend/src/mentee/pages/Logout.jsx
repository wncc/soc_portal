import React, { useEffect } from 'react';
import api from '../../utils/api';
import { useNavigate } from 'react-router-dom';
import { clearAuthData } from '../../utils/auth';

function Logout() {
  const navigate = useNavigate();
  
  useEffect(() => {
    const performLogout = async () => {
      try {
        // Call backend to clear server-side cookies
        await api.get(`${process.env.REACT_APP_BACKEND_URL}/accounts/logout/`);
      } catch (err) {
        console.log('Logout API error (continuing anyway):', err);
      } finally {
        // Always clear client-side data regardless of API result
        clearAuthData();
        navigate('/login');
        // Small delay before reload to ensure navigation completes
        setTimeout(() => {
          window.location.reload();
        }, 100);
      }
    };
    
    performLogout();
  }, [navigate]);

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      minHeight: '100vh', background: '#080c14', color: '#94a3b8',
      fontFamily: 'Inter, sans-serif',
    }}>
      Logging out...
    </div>
  );
}

export default Logout;
