import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import './DomainForm.css';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

export default function DomainForm({ domain, onClose, onSaved }) {
  const isEdit = !!domain;

  const [form, setForm] = useState({
    slug: '',
    name: '',
    description: '',
    order: 0,
    is_active: true,
    mentee_reg_open: false,
    mentor_reg_open: false,
    project_creation_open: true,
    project_editing_open: true,
  });
  const [coverFile, setCoverFile] = useState(null);
  const [coverPreview, setCoverPreview] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (domain) {
      setForm({
        slug: domain.slug || '',
        name: domain.name || '',
        description: domain.description || '',
        order: domain.order || 0,
        is_active: domain.is_active !== false,
        mentee_reg_open: domain.mentee_reg_open || false,
        mentor_reg_open: domain.mentor_reg_open || false,
        project_creation_open: domain.project_creation_open !== false,
        project_editing_open: domain.project_editing_open !== false,
      });
      if (domain.cover_photo_url) setCoverPreview(domain.cover_photo_url);
    }
  }, [domain]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setCoverFile(file);
    setCoverPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    const data = new FormData();
    Object.entries(form).forEach(([k, v]) => data.append(k, v));
    if (coverFile) data.append('cover_photo', coverFile);

    try {
      if (isEdit) {
        await api.patch(`${BACKEND}/domains/${domain.slug}/`, data, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else {
        await api.post(`${BACKEND}/domains/`, data, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }
      onSaved();
    } catch (err) {
      setError(
        err.response?.data
          ? JSON.stringify(err.response.data)
          : 'Failed to save domain'
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="df-overlay" onClick={onClose}>
      <div className="df-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="df-header">
          <h2>{isEdit ? `Edit: ${domain.name}` : 'New Domain'}</h2>
          <button className="df-close" onClick={onClose} aria-label="Close">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="df-form">
          {/* Cover photo */}
          <div className="df-cover-preview" style={{
            background: coverPreview
              ? `url(${coverPreview}) center/cover`
              : 'linear-gradient(135deg, #7c3aed44, #06b6d444)',
          }}>
            <label className="df-cover-btn" htmlFor="df-cover-input">
              📷 {coverPreview ? 'Change Photo' : 'Add Cover Photo'}
            </label>
            <input
              id="df-cover-input"
              type="file"
              accept="image/*"
              onChange={handleFile}
              style={{ display: 'none' }}
            />
          </div>

          {/* Fields */}
          <div className="df-fields">
            <div className="df-row">
              <div className="df-field">
                <label className="df-label">Slug <span className="df-required">*</span></label>
                <input
                  className="df-input"
                  name="slug"
                  placeholder="e.g. soq"
                  value={form.slug}
                  onChange={handleChange}
                  required
                  disabled={isEdit}
                  pattern="[a-z0-9-]+"
                  title="Lowercase letters, numbers, hyphens only"
                />
                <small className="df-hint">Short unique identifier (cannot be changed after creation)</small>
              </div>
              <div className="df-field">
                <label className="df-label">Display Order</label>
                <input
                  className="df-input"
                  name="order"
                  type="number"
                  min="0"
                  value={form.order}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="df-field">
              <label className="df-label">Name <span className="df-required">*</span></label>
              <input
                className="df-input"
                name="name"
                placeholder="e.g. Summer of Quants"
                value={form.name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="df-field">
              <label className="df-label">Description</label>
              <textarea
                className="df-textarea"
                name="description"
                placeholder="Describe what this domain is about..."
                rows={4}
                value={form.description}
                onChange={handleChange}
              />
            </div>

            <div className="df-field df-checkbox-field">
              <label className="df-checkbox-label">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={form.is_active}
                  onChange={handleChange}
                />
                <span>Active (visible on public home page)</span>
              </label>
            </div>

            <div className="df-field">
              <label className="df-label">Registration Settings</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' }}>
                <label className="df-checkbox-label">
                  <input
                    type="checkbox"
                    name="mentee_reg_open"
                    checked={form.mentee_reg_open}
                    onChange={handleChange}
                  />
                  <span>✅ Mentee Registration Open (auto-approved)</span>
                </label>
                <label className="df-checkbox-label">
                  <input
                    type="checkbox"
                    name="mentor_reg_open"
                    checked={form.mentor_reg_open}
                    onChange={handleChange}
                  />
                  <span>⏳ Mentor Registration Open (requires approval)</span>
                </label>
              </div>
            </div>

            <div className="df-field">
              <label className="df-label">Mentor Project Permissions</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' }}>
                <label className="df-checkbox-label">
                  <input
                    type="checkbox"
                    name="project_creation_open"
                    checked={form.project_creation_open}
                    onChange={handleChange}
                  />
                  <span>📝 Allow mentors to create new projects</span>
                </label>
                <label className="df-checkbox-label">
                  <input
                    type="checkbox"
                    name="project_editing_open"
                    checked={form.project_editing_open}
                    onChange={handleChange}
                  />
                  <span>✏️ Allow mentors to edit existing projects</span>
                </label>
              </div>
            </div>
          </div>

          {error && <div className="df-error">{error}</div>}

          <div className="df-actions">
            <button type="button" className="df-btn-ghost" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="df-btn-save" disabled={saving}>
              {saving ? 'Saving…' : isEdit ? 'Save Changes' : 'Create Domain'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
