import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import DomainForm from './DomainForm';
import MembersPanel from './MembersPanel';
import './ManagerDashboard.css';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

export default function ManagerDashboard() {
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editDomain, setEditDomain] = useState(null);
  const [managingDomain, setManagingDomain] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const navigate = useNavigate();



  const fetchDomains = useCallback(async () => {
    try {
      const res = await api.get(`${BACKEND}/domains/all/`);
      setDomains(res.data);
    } catch (e) {
      console.error('Failed to fetch domains', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDomains();
  }, [fetchDomains]);

  const handleDelete = async (slug) => {
    try {
      await api.delete(`${BACKEND}/domains/${slug}/`);
      setDeleteConfirm(null);
      fetchDomains();
    } catch (e) {
      alert('Failed to delete domain: ' + (e.response?.data?.error || e.message));
    }
  };

  const openPortal = (domainSlug, view) => {
    if (view === 'mentee') window.open(`/${domainSlug}/current_projects`, '_blank');
    else if (view === 'mentor') window.open(`/${domainSlug}/mentor/home`, '_blank');
    else {
      window.open(`/${domainSlug}/current_projects`, '_blank');
      window.open(`/${domainSlug}/mentor/home`, '_blank');
    }
  };

  return (
    <div className="mgr-root-new">
      {/* Main Content */}
      <main className="mgr-main-new">
        {/* Header */}
        <header className="mgr-header">
          <div>
            <h1 className="mgr-header-title">Domains</h1>
            <p className="mgr-header-sub">
              Manage Summer of Tech domains — SOC, SOQ, SOR and more
            </p>
          </div>
          <button
            className="mgr-btn-new"
            onClick={() => { setEditDomain(null); setShowForm(true); }}
          >
            + New Domain
          </button>
        </header>

        {/* Stats row */}
        <div className="mgr-stats">
          <StatCard label="Total Domains" value={domains.length} icon="🌐" />
          <StatCard
            label="Active Domains"
            value={domains.filter((d) => d.is_active).length}
            icon="✅"
          />
          <StatCard
            label="Total Members"
            value={domains.reduce((s, d) => s + (d.member_count || 0), 0)}
            icon="👥"
          />
        </div>

        {/* Domains list */}
        {loading ? (
          <div className="mgr-loading">
            <div className="mgr-spinner" />
          </div>
        ) : domains.length === 0 ? (
          <div className="mgr-empty">
            <div className="mgr-empty-icon">🌐</div>
            <h3>No domains yet</h3>
            <p>Create your first domain to get started</p>
            <button className="mgr-btn-new" onClick={() => setShowForm(true)}>
              + Create Domain
            </button>
          </div>
        ) : (
          <div className="mgr-domain-list">
            {domains.map((domain) => (
              <DomainRow
                key={domain.slug}
                domain={domain}
                onEdit={() => { setEditDomain(domain); setShowForm(true); }}
                onDelete={() => setDeleteConfirm(domain.slug)}
                onMembers={() => setManagingDomain(domain)}
                onOpenPortal={(view) => openPortal(domain.slug, view)}
              />
            ))}
          </div>
        )}
      </main>

      {/* Domain form modal */}
      {showForm && (
        <DomainForm
          domain={editDomain}
          onClose={() => { setShowForm(false); setEditDomain(null); }}
          onSaved={() => { setShowForm(false); setEditDomain(null); fetchDomains(); }}
        />
      )}

      {/* Members panel modal */}
      {managingDomain && (
        <MembersPanel
          domain={managingDomain}
          onClose={() => setManagingDomain(null)}
        />
      )}

      {/* Delete confirmation */}
      {deleteConfirm && (
        <div className="mgr-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="mgr-confirm" onClick={(e) => e.stopPropagation()}>
            <h3>Deactivate Domain?</h3>
            <p>
              The domain <strong>{deleteConfirm}</strong> will be hidden from the public.
              All existing data (projects, mentor/mentee records) will be preserved.
            </p>
            <div className="mgr-confirm-actions">
              <button className="mgr-btn-ghost" onClick={() => setDeleteConfirm(null)}>
                Cancel
              </button>
              <button
                className="mgr-btn-danger"
                onClick={() => handleDelete(deleteConfirm)}
              >
                Deactivate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, icon }) {
  return (
    <div className="mgr-stat">
      <span className="mgr-stat-icon">{icon}</span>
      <div>
        <div className="mgr-stat-value">{value}</div>
        <div className="mgr-stat-label">{label}</div>
      </div>
    </div>
  );
}

function DomainRow({ domain, onEdit, onDelete, onMembers, onOpenPortal }) {
  const [portalOpen, setPortalOpen] = useState(false);

  const slugColors = {
    soc: '#7c3aed', soq: '#0ea5e9', sor: '#f59e0b',
  };
  const color = slugColors[domain.slug] || '#10b981';

  return (
    <div className={`mgr-row ${!domain.is_active ? 'mgr-row-inactive' : ''}`}>
      {/* Color bar */}
      <div className="mgr-row-bar" style={{ background: color }} />

      {/* Cover thumb */}
      <div
        className="mgr-row-thumb"
        style={{
          background: domain.cover_photo_url
            ? `url(${domain.cover_photo_url}) center/cover`
            : `linear-gradient(135deg, ${color}33, ${color}66)`,
        }}
      />

      {/* Info */}
      <div className="mgr-row-info">
        <div className="mgr-row-top">
          <h3 className="mgr-row-name">{domain.name}</h3>
          <span className="mgr-row-slug">{domain.slug.toUpperCase()}</span>
          {!domain.is_active && <span className="mgr-row-inactive-badge">Inactive</span>}
        </div>
        <p className="mgr-row-desc">
          {domain.description
            ? domain.description.length > 100
              ? domain.description.slice(0, 100) + '…'
              : domain.description
            : '—'}
        </p>
        <div className="mgr-row-meta">
          <span>👥 {domain.member_count} members</span>
          <span>📝 Create: {domain.project_creation_open ? '✅' : '❌'}</span>
          <span>✏️ Edit: {domain.project_editing_open ? '✅' : '❌'}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="mgr-row-actions">
        {/* Open Portal dropdown */}
        <div className="mgr-portal-wrap">
          <button
            className="mgr-btn-portal"
            onClick={() => setPortalOpen((v) => !v)}
          >
            Open Portal ▾
          </button>
          {portalOpen && (
            <div className="mgr-portal-menu" onMouseLeave={() => setPortalOpen(false)}>
              <button onClick={() => { onOpenPortal('mentee'); setPortalOpen(false); }}>
                👤 Mentee Portal
              </button>
              <button onClick={() => { onOpenPortal('mentor'); setPortalOpen(false); }}>
                🎓 Mentor Portal
              </button>
              <button onClick={() => { onOpenPortal('both'); setPortalOpen(false); }}>
                🪟 Both Portals
              </button>
            </div>
          )}
        </div>

        <button className="mgr-btn-members" onClick={onMembers} title="Manage Members">
          👥 Members
        </button>
        <button className="mgr-btn-edit" onClick={onEdit} title="Edit Domain">
          ✏ Edit
        </button>
        <button className="mgr-btn-del" onClick={onDelete} title="Deactivate Domain">
          🗑
        </button>
      </div>
    </div>
  );
}
