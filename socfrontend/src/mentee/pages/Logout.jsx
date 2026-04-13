import React, { useEffect } from 'react';
import api from '../../utils/api';
import { useNavigate } from 'react-router-dom';
import { clearAuthData } from '../../utils/auth';

function Logout() {
  const navigate = useNavigate();
  
  useEffect(() => {
    api.get(`${process.env.REACT_APP_BACKEND_URL}/accounts/logout/`)
      .then((res) => {
        clearAuthData();
        navigate('/login');
        window.location.reload();
      })
      .catch(err => {
        console.log('Logout error:', err);
        // Clear data even if API call fails
        clearAuthData();
        navigate('/login');
        window.location.reload();
      });
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
