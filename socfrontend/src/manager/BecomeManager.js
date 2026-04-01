import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';

const BACKEND = process.env.REACT_APP_BACKEND_URL;
const SSO_PROJECT_ID = '38dd0ef6-28a1-4a14-980e-b294bd987636';

/**
 * BecomeManager page: /become-manager/:secret
 *
 * Flow:
 *   1. Not logged in  → save secret to sessionStorage → redirect straight to ITC SSO
 *   2. SSO callback lands on /loading → completes login → Loading.jsx checks
 *      sessionStorage for a pending become-manager redirect → goes here
 *   3. Logged in here → call backend → get manager role → redirect to /manager
 */
export default function BecomeManager() {
  const { secret } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('checking'); // checking | granting | success | error

  const isLoggedIn = () => !!localStorage.getItem('authToken');

  const redirectToSSO = () => {
    // Save the intended destination so Loading.jsx can redirect back after login
    sessionStorage.setItem('post_login_redirect', `/become-manager/${secret}`);

    // Build the SSO callback URL → /loading (which handles token exchange)
    const frontendBase = (process.env.REACT_APP_FRONTEND_URL || window.location.origin).replace(/\/$/, '');
    const redirect = encodeURIComponent(`${frontendBase}/loading`);
    window.location.href = `https://sso.tech-iitb.org/project/${SSO_PROJECT_ID}/ssocall/?redirect=${redirect}`;
  };

  const grantManagerRole = async () => {
    setStatus('granting');
    try {
      const res = await api.get(`${BACKEND}/accounts/become-manager/${secret}/`);
      localStorage.setItem('is_manager', 'true');
      setStatus('success');
      setTimeout(() => navigate('/manager'), 1800);
    } catch (err) {
      const msg = err.response?.data?.error || 'Invalid or expired token.';
      setStatus(msg.includes('403') || err.response?.status === 403 ? 'forbidden' : 'error');
    }
  };

  useEffect(() => {
    if (!isLoggedIn()) {
      // Not logged in → go straight to SSO, don't show the login page at all
      setStatus('redirecting');
      // Small delay so the spinner is visible before SSO redirect
      const t = setTimeout(redirectToSSO, 600);
      return () => clearTimeout(t);
    }
    // Already logged in → immediately try to get manager role
    grantManagerRole();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const S = {
    root: {
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#080c14',
      fontFamily: "'Inter', sans-serif",
      padding: '24px',
    },
    card: {
      background: '#0f1624',
      border: '1px solid rgba(255,255,255,0.07)',
      borderRadius: '20px',
      padding: '52px 48px',
      maxWidth: '440px',
      width: '100%',
      textAlign: 'center',
      boxShadow: '0 24px 80px rgba(0,0,0,0.5)',
    },
    icon: { fontSize: '3rem', marginBottom: '20px', display: 'block' },
    title: { color: '#f0f4ff', fontSize: '1.35rem', fontWeight: 700, margin: '0 0 12px', fontFamily: "'Space Grotesk', sans-serif" },
    msg: { color: '#94a3b8', fontSize: '0.95rem', lineHeight: 1.6, margin: 0 },
    spinner: {
      width: 44, height: 44,
      borderRadius: '50%',
      border: '3px solid rgba(124,58,237,0.2)',
      borderTopColor: '#7c3aed',
      animation: 'bm-spin 0.8s linear infinite',
      margin: '0 auto 24px',
    },
    pill: {
      display: 'inline-block',
      background: 'rgba(124,58,237,0.12)',
      border: '1px solid rgba(124,58,237,0.3)',
      color: '#a78bfa',
      borderRadius: '999px',
      fontSize: '0.72rem',
      fontWeight: 700,
      letterSpacing: '0.1em',
      textTransform: 'uppercase',
      padding: '5px 14px',
      marginBottom: '24px',
    },
  };

  const CONTENT = {
    checking: {
      spinner: true,
      title: 'Checking session…',
      msg: 'One moment while we verify your login.',
    },
    redirecting: {
      spinner: true,
      title: 'Redirecting to ITC SSO…',
      msg: 'You\'ll be sent to SSO to log in, then automatically returned here to gain manager access.',
    },
    granting: {
      spinner: true,
      title: 'Granting Manager Access…',
      msg: 'Authenticating with the Summer of Tech platform.',
    },
    success: {
      icon: '🎉',
      title: 'Welcome, Manager!',
      msg: 'You now have platform manager access. Redirecting to your dashboard…',
    },
    error: {
      icon: '❌',
      title: 'Something went wrong',
      msg: 'The token may be invalid or expired. Contact the ITC team.',
    },
    forbidden: {
      icon: '🚫',
      title: 'Access Denied',
      msg: 'Invalid or expired manager token. Make sure you\'re using the correct link.',
    },
  };

  const view = CONTENT[status] || CONTENT.checking;

  return (
    <div style={S.root}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');
        @keyframes bm-spin { to { transform: rotate(360deg); } }
      `}</style>
      <div style={S.card}>
        <span style={S.pill}>ITC · Summer of Tech</span>
        {view.spinner ? (
          <div style={S.spinner} />
        ) : (
          <span style={S.icon}>{view.icon}</span>
        )}
        <h1 style={S.title}>{view.title}</h1>
        <p style={S.msg}>{view.msg}</p>
      </div>
    </div>
  );
}
