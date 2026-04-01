import React from 'react';

export default function DebugMemberships() {
  const memberships = localStorage.getItem('memberships');
  const role = localStorage.getItem('role');
  const authToken = localStorage.getItem('authToken');
  const isManager = localStorage.getItem('is_manager');

  let parsed = null;
  try {
    parsed = JSON.parse(memberships || '[]');
  } catch (e) {
    parsed = 'ERROR PARSING';
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Debug: LocalStorage Contents</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h3>authToken:</h3>
        <pre>{authToken || 'null'}</pre>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>role (legacy):</h3>
        <pre>{role || 'null'}</pre>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>is_manager:</h3>
        <pre>{isManager || 'null'}</pre>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>memberships (raw string):</h3>
        <pre>{memberships || 'null'}</pre>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>memberships (parsed):</h3>
        <pre>{JSON.stringify(parsed, null, 2)}</pre>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>Test Domain Access:</h3>
        {Array.isArray(parsed) && parsed.map((m, i) => (
          <div key={i} style={{ padding: '10px', border: '1px solid #ccc', marginBottom: '10px' }}>
            <strong>Domain:</strong> {m.domain || 'null'}<br />
            <strong>Domain Name:</strong> {m.domain_name || 'null'}<br />
            <strong>Role:</strong> {m.role || 'null'}<br />
            <strong>Approved:</strong> {m.is_approved ? 'Yes' : 'No'}<br />
            <br />
            <a href={`/${m.domain}/mentor/home`}>Try Mentor Portal</a> | 
            <a href={`/${m.domain}/current_projects`}> Try Mentee Portal</a>
          </div>
        ))}
      </div>
    </div>
  );
}
