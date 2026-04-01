import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import './SummerOfTech.css';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

export default function SummerOfTech({ authToken }) {
  const [domains, setDomains] = useState([]);
  const [memberships, setMemberships] = useState([]);
  const [isManager, setIsManager] = useState(false);
  const [loading, setLoading] = useState(true);
  const [roleModal, setRoleModal] = useState(null); // { domain, options: [{ role, action, label }] }
  const navigate = useNavigate();

  const fetchDomains = useCallback(async () => {
    try {
      const res = await api.get(`${BACKEND}/domains/`);
      setDomains(res.data);
    } catch (e) {
      console.error('Failed to fetch domains', e);
    }
  }, []);

  const fetchMemberships = useCallback(async () => {
    if (!authToken) return;
    try {
      const res = await api.get(`${BACKEND}/accounts/my-memberships/`);
      setMemberships(res.data.memberships || []);
      
      // Update local state and sync to localStorage for routing guards
      const managerFlag = res.data.is_manager || false;
      setIsManager(managerFlag);
      localStorage.setItem('is_manager', managerFlag ? 'true' : 'false');
    } catch (e) {
      console.error('Failed to fetch memberships', e);
    }
  }, [authToken]);

  useEffect(() => {
    Promise.all([fetchDomains(), fetchMemberships()]).finally(() => setLoading(false));
  }, [fetchDomains, fetchMemberships]);

  const getMyRoles = (domainSlug) =>
    memberships
      .filter((m) => m.domain === domainSlug && m.is_approved)
      .map((m) => m.role);

  const handleDomainClick = (domain) => {
    if (!authToken) {
      navigate('/login');
      return;
    }
    
    const roles = getMyRoles(domain.slug);
    
    // Always show role selection modal for logged-in users
    // If they have roles, show "Open Portal" options
    // If they don't have roles, show "Apply" options
    const availableOptions = [];
    
    if (roles.includes('mentor')) {
      availableOptions.push({ role: 'mentor', action: 'open', label: 'Open Mentor Portal' });
    } else if (domain.mentor_reg_open) {
      availableOptions.push({ role: 'mentor', action: 'apply', label: 'Apply as Mentor' });
    }
    
    if (roles.includes('mentee')) {
      availableOptions.push({ role: 'mentee', action: 'open', label: 'Open Mentee Portal' });
    } else if (domain.mentee_reg_open) {
      availableOptions.push({ role: 'mentee', action: 'apply', label: 'Register as Mentee' });
    }
    
    if (availableOptions.length === 0) {
      alert('Registration is currently closed for this domain.');
      return;
    }
    
    setRoleModal({ domain, options: availableOptions });
  };

  const handleLogin = () => navigate('/login');

  const handleModalAction = async (domain, role, action) => {
    if (action === 'open') {
      setRoleModal(null);
      if (role === 'mentor') {
        navigate(`/${domain.slug}/mentor/home`);
      } else {
        navigate(`/${domain.slug}/current_projects`);
      }
    } else if (action === 'apply') {
      try {
        await api.post(`${BACKEND}/domains/${domain.slug}/members/`, { role });
        setRoleModal(null);
        if (role === 'mentee') {
          alert('Successfully registered as mentee! You can now browse projects.');
          navigate(`/${domain.slug}/current_projects`);
        } else {
          alert('Successfully applied as mentor! Your application is pending approval.');
          fetchMemberships();
        }
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to apply');
      }
    }
  };

  const roleBadgeClass = (role) => {
    const map = { manager: 'badge-manager', mentor: 'badge-mentor', mentee: 'badge-mentee' };
    return `sot-badge ${map[role] || 'badge-other'}`;
  };

  if (loading) {
    return (
      <div className="sot-loading">
        <div className="sot-loader" />
      </div>
    );
  }

  return (
    <div className="sot-root" style={{ paddingTop: '72px' }}>
      {/* Hero */}
      <section className="sot-hero">
        <div className="sot-hero-glow" aria-hidden="true" />
        <div className="sot-hero-content">
          <div className="sot-hero-badge">IIT Bombay · ITC</div>
          <h1 className="sot-hero-title">
            Summer of <span className="sot-hero-accent">Tech</span>
          </h1>
          <p className="sot-hero-sub">
            Explore projects across Coding, Quants, Robotics and more. Find your domain. Build something extraordinary.
          </p>
          {!authToken ? (
            <button className="sot-btn-primary" onClick={handleLogin}>
              Login with ITC SSO
              <span className="sot-btn-arrow">→</span>
            </button>
          ) : (
            <div className="sot-hero-actions">
              {isManager && (
                <button className="sot-btn-manager" onClick={() => navigate('/manager')}>
                  ⚙ Manager Dashboard
                </button>
              )}
              {memberships.length > 0 && (
                <p className="sot-hero-welcome">
                  You're enrolled in {memberships.filter((m) => m.is_approved).length} domain{memberships.length !== 1 ? 's' : ''}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Floating orbs */}
        <div className="sot-orb sot-orb-1" aria-hidden="true" />
        <div className="sot-orb sot-orb-2" aria-hidden="true" />
        <div className="sot-orb sot-orb-3" aria-hidden="true" />
      </section>

      {/* My Memberships strip (if logged in) */}
      {authToken && memberships.filter((m) => m.is_approved).length > 0 && (
        <section className="sot-my-section">
          <div className="sot-my-inner">
            <h2 className="sot-my-title">Your Memberships</h2>
            <div className="sot-my-chips">
              {memberships
                .filter((m) => m.is_approved)
                .map((m, i) => (
                  <button
                    key={i}
                    className="sot-my-chip"
                    onClick={() => m.domain && handleDomainClick({ slug: m.domain })}
                  >
                    <span className="sot-my-chip-domain">{m.domain_name || 'Platform'}</span>
                    <span className={roleBadgeClass(m.role)}>{m.role}</span>
                  </button>
                ))}
            </div>
          </div>
        </section>
      )}

      {/* Domains Grid */}
      <section className="sot-domains-section">
        <div className="sot-domains-inner">
          <div className="sot-section-header">
            <h2 className="sot-section-title">Explore Domains</h2>
            <p className="sot-section-sub">
              Each domain runs independently with its own mentors, mentees, and projects.
            </p>
          </div>

          {domains.length === 0 ? (
            <div className="sot-empty">
              <p>No domains published yet. Check back soon!</p>
            </div>
          ) : (
            <div className="sot-grid">
              {domains.map((domain) => {
                const myRoles = getMyRoles(domain.slug);
                return (
                  <DomainCard
                    key={domain.slug}
                    domain={domain}
                    myRoles={myRoles}
                    authToken={authToken}
                    onClick={() => handleDomainClick(domain)}
                  />
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="sot-footer">
        <p>© {new Date().getFullYear()} ITC, IIT Bombay · Web & Coding Club · Summer of Tech</p>
      </footer>

      {/* Role Selection Modal */}
      {roleModal && (
        <div className="sot-modal-overlay" onClick={() => setRoleModal(null)}>
          <div className="sot-modal" onClick={(e) => e.stopPropagation()}>
            <h3 className="sot-modal-title">{roleModal.domain.name}</h3>
            <p className="sot-modal-desc">
              Choose how you want to participate in this domain:
            </p>
            <div className="sot-modal-actions">
              {roleModal.options.map((option, idx) => (
                <button
                  key={idx}
                  className={`sot-modal-btn ${
                    option.role === 'mentor' ? 'sot-modal-btn-mentor' : 'sot-modal-btn-mentee'
                  }`}
                  onClick={() => handleModalAction(roleModal.domain, option.role, option.action)}
                >
                  {option.role === 'mentor' ? '🎓' : '👤'} {option.label}
                  {option.action === 'apply' && (
                    <span style={{ fontSize: '0.75rem', display: 'block', marginTop: '4px', opacity: 0.8 }}>
                      {option.role === 'mentor' ? 'Requires approval' : 'Browse & apply to projects'}
                    </span>
                  )}
                </button>
              ))}
            </div>
            <button className="sot-modal-close" onClick={() => setRoleModal(null)}>
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function DomainCard({ domain, myRoles, authToken, onClick }) {
  const [hovered, setHovered] = useState(false);

  const slugColors = {
    soc: { from: '#6366f1', to: '#8b5cf6' },
    soq: { from: '#06b6d4', to: '#0ea5e9' },
    sor: { from: '#f59e0b', to: '#ef4444' },
  };
  const colors = slugColors[domain.slug] || { from: '#10b981', to: '#059669' };

  return (
    <div
      className={`sot-card ${hovered ? 'sot-card-hovered' : ''}`}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
      aria-label={`Open ${domain.name}`}
    >
      {/* Cover */}
      <div
        className="sot-card-cover"
        style={{
          background: domain.cover_photo_url
            ? `url(${domain.cover_photo_url}) center/cover`
            : `linear-gradient(135deg, ${colors.from}, ${colors.to})`,
        }}
      >
        <div className="sot-card-cover-overlay" />
        <div className="sot-card-slug">{domain.slug.toUpperCase()}</div>

        {/* My role badges in this domain */}
        {myRoles.length > 0 && (
          <div className="sot-card-role-badges">
            {myRoles.map((role) => (
              <span key={role} className={`sot-card-role-badge sot-card-role-${role}`}>
                {role}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Body */}
      <div className="sot-card-body">
        <h3 className="sot-card-name">{domain.name}</h3>
        <p className="sot-card-desc">
          {domain.description
            ? domain.description.length > 120
              ? domain.description.slice(0, 120) + '…'
              : domain.description
            : 'A new domain under Summer of Tech.'}
        </p>

        <div className="sot-card-footer">
          <span className="sot-card-count">
            {domain.member_count} member{domain.member_count !== 1 ? 's' : ''}
          </span>
          
          {/* Registration status badges */}
          <div className="sot-card-reg-status">
            {domain.mentee_reg_open && (
              <span className="sot-reg-badge sot-reg-open">Mentee: Open</span>
            )}
            {domain.mentor_reg_open && (
              <span className="sot-reg-badge sot-reg-open">Mentor: Open</span>
            )}
          </div>

          {!authToken ? (
            <span className="sot-card-cta">Login to explore →</span>
          ) : (
            <span className="sot-card-cta sot-card-cta-enrolled">Explore →</span>
          )}
        </div>
      </div>
    </div>
  );
}
