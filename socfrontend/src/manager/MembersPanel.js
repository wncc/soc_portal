import React, { useEffect, useState } from 'react';
import api from '../utils/api';
import './MembersPanel.css';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

const ROLE_COLORS = {
  manager: '#f59e0b',
  mentor: '#10b981',
  mentee: '#6366f1',
};

export default function MembersPanel({ domain, onClose }) {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('all'); // 'all' | 'mentor' | 'mentee' | 'pending'

  const fetchMembers = async () => {
    try {
      const res = await api.get(`${BACKEND}/domains/${domain.slug}/members/`);
      setMembers(res.data);
    } catch (e) {
      console.error('Failed to fetch members', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchMembers(); }, [domain.slug]);

  const handleApprove = async (id) => {
    try {
      await api.patch(`${BACKEND}/domains/${domain.slug}/members/${id}/`);
      fetchMembers();
    } catch (e) {
      alert('Failed to approve: ' + (e.response?.data?.error || e.message));
    }
  };

  const handleRemove = async (id) => {
    if (!window.confirm('Remove this membership?')) return;
    try {
      await api.delete(`${BACKEND}/domains/${domain.slug}/members/${id}/`);
      fetchMembers();
    } catch (e) {
      alert('Failed to remove: ' + (e.response?.data?.error || e.message));
    }
  };

  const filtered = members.filter((m) => {
    if (tab === 'pending') return !m.is_approved;
    if (tab === 'all') return true;
    return m.role === tab;
  });

  const pendingCount = members.filter((m) => !m.is_approved).length;

  return (
    <div className="mp-overlay" onClick={onClose}>
      <div className="mp-panel" onClick={(e) => e.stopPropagation()}>
        <div className="mp-header">
          <div>
            <h2 className="mp-title">Members — {domain.name}</h2>
            <p className="mp-sub">{members.length} total memberships</p>
          </div>
          <button className="mp-close" onClick={onClose}>✕</button>
        </div>

        {/* Tabs */}
        <div className="mp-tabs">
          {['all', 'mentor', 'mentee', 'manager', 'pending'].map((t) => (
            <button
              key={t}
              className={`mp-tab ${tab === t ? 'mp-tab-active' : ''}`}
              onClick={() => setTab(t)}
            >
              {t.charAt(0).toUpperCase() + t.slice(1)}
              {t === 'pending' && pendingCount > 0 && (
                <span className="mp-badge">{pendingCount}</span>
              )}
            </button>
          ))}
        </div>

        {/* List */}
        {loading ? (
          <div className="mp-loading"><div className="mp-spinner" /></div>
        ) : filtered.length === 0 ? (
          <div className="mp-empty">No members in this category.</div>
        ) : (
          <div className="mp-list">
            {filtered.map((m) => (
              <div key={m.id} className={`mp-item ${!m.is_approved ? 'mp-item-pending' : ''}`}>
                <div className="mp-item-left">
                  <div className="mp-avatar">
                    {m.username?.charAt(0).toUpperCase() || '?'}
                  </div>
                  <div>
                    <div className="mp-username">{m.username}</div>
                    <div className="mp-joined">Joined {new Date(m.joined).toLocaleDateString()}</div>
                  </div>
                </div>
                <div className="mp-item-right">
                  <span
                    className="mp-role-badge"
                    style={{ color: ROLE_COLORS[m.role], borderColor: ROLE_COLORS[m.role] + '44', background: ROLE_COLORS[m.role] + '15' }}
                  >
                    {m.role}
                  </span>
                  {!m.is_approved && (
                    <button className="mp-btn-approve" onClick={() => handleApprove(m.id)}>
                      ✓ Approve
                    </button>
                  )}
                  <button className="mp-btn-remove" onClick={() => handleRemove(m.id)} title="Remove membership">
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
