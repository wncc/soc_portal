import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import { clearAuthData, saveAuthData } from '../../utils/auth';

const Loading = () => {
  const navigate = useNavigate();

  const departmentMap = {
    AE: 'Aerospace Engineering', BS: 'Biosciences and Bioengineering',
    CH: 'Chemical Engineering', CY: 'Chemistry', CE: 'Civil Engineering',
    CSE: 'Computer Science and Engineering', ES: 'Earth Sciences',
    ECON: 'Economics', EE: 'Electrical Engineering', EN: 'Energy Science and Engineering',
    EP: 'Engineering Physics', EV: 'Environmental Science and Engineering',
    HSS: 'Humanities and Social Sciences', IDC: 'Industrial Design Centre',
    MA: 'Mathematics', ME: 'Mechanical Engineering',
    MM: 'Metallurgical Engineering and Materials Science',
    PH: 'Physics', IEOR: 'Industrial Engineering and Operations Research', OTHER: 'Other',
  };

  function getYearChoice(degree, passingYear) {
    const yearsLeft = passingYear - new Date().getFullYear();
    if (degree === 'B.Tech') {
      if (yearsLeft === 4) return 'First Year';
      if (yearsLeft === 3) return 'Second Year';
      if (yearsLeft === 2) return 'Third Year';
      if (yearsLeft === 1) return 'Fourth Year';
      return 'Fifth Year';
    }
    if (degree === 'M.Tech') return 'M.Tech';
    if (degree === 'Ph.D.') return 'Ph.D.';
    return 'Other';
  }

  const handleRedirect = (memberships, isManager) => {
    // If a specific post-login destination was saved (e.g. /become-manager/:secret),
    // honour it before doing the default membership-based routing.
    const pending = sessionStorage.getItem('post_login_redirect');
    if (pending) {
      sessionStorage.removeItem('post_login_redirect');
      navigate(pending);
      return;
    }

    // Always redirect to home page after login
    // User can then choose which domain/role to access
    navigate('/');
    window.location.reload(); // Force refresh to update App.js state
  };

  useEffect(() => {
    const accessid = localStorage.getItem('accessid');
    if (!accessid) { 
      console.log('[LOADING] No access ID found in localStorage');
      // Check URL params as fallback
      const params = new URLSearchParams(window.location.search);
      const urlAccessId = params.get('accessid');
      if (urlAccessId) {
        console.log('[LOADING] Found accessid in URL params');
        localStorage.setItem('accessid', urlAccessId);
      } else {
        console.error('[LOADING] No access ID found - redirecting to login');
        navigate('/login'); 
        return;
      }
    }

    const doSSOLogin = async () => {
      try {
        const currentAccessId = localStorage.getItem('accessid');
        console.log('[LOADING] Starting SSO login with accessid:', currentAccessId?.substring(0, 20) + '...');
        
        // Step 1: Fetch SSO user data
        const ssoRes = await api.post(
          `${process.env.REACT_APP_BACKEND_URL}/accounts/get-sso-user/`, { accessid: currentAccessId }
        );
        const user = ssoRes.data;
        console.log('[LOADING] SSO user data received:', user.roll);
        const department = departmentMap[user.department] || 'Other';
        const year = getYearChoice(user.degree, user.passing_year);

        // Step 2: Register user (no role param — one user record per roll number)
        const formData = new FormData();
        formData.append('name', user.name);
        formData.append('roll_number', user.roll);
        formData.append('phone_number', '0000000000');
        formData.append('password', user.roll.toLowerCase());
        formData.append('year', year);
        formData.append('department', department);

        try {
          await api.post(`${process.env.REACT_APP_BACKEND_URL}/accounts/register_sso/`, formData);
          console.log('[LOADING] User registered successfully');
        } catch (err) {
          if (err.response?.data?.error !== 'User already exists') {
            console.error('[LOADING] Registration failed:', err);
            alert('Registration failed. Try again.');
            clearAuthData();
            navigate('/login');
            return;
          }
          console.log('[LOADING] User already exists, continuing to login');
          // User already exists — continue to login
        }

        // Step 3: Get auth token (no role param in new architecture)
        const loginForm = new FormData();
        loginForm.append('username', user.roll);
        loginForm.append('password', user.roll.toLowerCase());
        
        let loginRes;
        try {
          console.log('[LOADING] Requesting auth token...');
          loginRes = await api.post(
            `${process.env.REACT_APP_BACKEND_URL}/accounts/token_sso/`, loginForm
          );
          console.log('[LOADING] Auth token received');
        } catch (loginErr) {
          console.error('[LOADING] Token generation failed:', loginErr);
          clearAuthData();
          alert('Login failed. Please try again.');
          navigate('/login');
          return;
        }

        // Only save to localStorage if login was successful
        if (!loginRes || !loginRes.data || !loginRes.data.access) {
          console.error('Invalid login response:', loginRes);
          clearAuthData();
          alert('Login failed. Invalid response from server.');
          navigate('/login');
          return;
        }

        const token = loginRes.data.access;
        const memberships = loginRes.data.memberships || [];
        const isManager = loginRes.data.is_manager || false;

        // Save to localStorage only after successful login
        const saved = saveAuthData(token, memberships, isManager);
        if (!saved) {
          alert('Failed to save login data. Please try again.');
          navigate('/login');
          return;
        }
        
        console.log('[LOADING] Auth data saved successfully');
        localStorage.removeItem('accessid');

        handleRedirect(memberships, isManager);
      } catch (err) {
        console.error('[LOADING] SSO Login Failed:', err);
        console.error('[LOADING] Error details:', err.response?.data || err.message);
        // Clean up ALL localStorage data on failure
        clearAuthData();
        alert(`SSO Login failed: ${err.response?.data?.error || err.message || 'Unknown error'}`);
        navigate('/login');
      }
    };

    doSSOLogin();
  }, [navigate]);

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      minHeight: '100vh', background: '#080c14', flexDirection: 'column', gap: '16px',
      fontFamily: 'Inter, sans-serif',
    }}>
      <div style={{
        width: 48, height: 48, borderRadius: '50%',
        border: '3px solid rgba(124,58,237,0.2)', borderTopColor: '#7c3aed',
        animation: 'spin 0.8s linear infinite',
      }} />
      <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>Logging you in via ITC SSO…</p>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default Loading;
