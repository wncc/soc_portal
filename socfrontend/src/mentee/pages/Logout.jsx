import React, { useEffect } from 'react';
import api from '../../utils/api';
import { useNavigate } from 'react-router-dom';

function Logout() {
  const navigate = useNavigate();
  useEffect(() => {
    api.get('https://socb.tech-iitb.org/api/accounts/logout/')
      .then((res) => {
        // console.log(res.data);
        window.location.reload();
        localStorage.removeItem('authToken');
        localStorage.removeItem('role');
        navigate('/login');
                
      })
      .catch(err => {
        console.log(err);
        window.location.reload();
        localStorage.removeItem('authToken');
        localStorage.removeItem('role');
        navigate('/login');
              
      });
  }, []);

  return (
    <div>Logout</div>
  );
}

export default Logout;
