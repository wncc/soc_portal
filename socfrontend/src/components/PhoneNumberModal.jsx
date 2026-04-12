// PhoneNumberModal.jsx
// Place this in: socfrontend/src/components/PhoneNumberModal.jsx

import React, { useState } from 'react';
import './PhoneNumberModal.css'; // Create corresponding CSS file

const PhoneNumberModal = ({ onClose }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validatePhone = (phone) => {
    // Indian phone number validation (10 digits)
    const phoneRegex = /^[6-9]\d{9}$/;
    return phoneRegex.test(phone);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate
    if (!phoneNumber.trim()) {
      setError('Phone number is required');
      return;
    }
    
    if (!validatePhone(phoneNumber)) {
      setError('Please enter a valid 10-digit phone number');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/accounts/profile/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important for cookie-based auth
        body: JSON.stringify({ phone_number: phoneNumber }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Phone number updated:', data);
        onClose(); // Close modal on success
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to update phone number');
      }
    } catch (err) {
      console.error('Error updating phone number:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePhoneChange = (e) => {
    const value = e.target.value.replace(/\D/g, ''); // Remove non-digits
    if (value.length <= 10) {
      setPhoneNumber(value);
      setError('');
    }
  };

  return (
    <div className="phone-modal-overlay">
      <div className="phone-modal-container">
        <div className="phone-modal-header">
          <h2>📱 Update Your Phone Number</h2>
          <p>Please provide your phone number to continue</p>
        </div>

        <form onSubmit={handleSubmit} className="phone-modal-form">
          <div className="form-group">
            <label htmlFor="phone">Phone Number</label>
            <input
              id="phone"
              type="tel"
              value={phoneNumber}
              onChange={handlePhoneChange}
              placeholder="Enter 10-digit phone number"
              className={error ? 'input-error' : ''}
              disabled={loading}
              autoFocus
            />
            {error && <span className="error-message">{error}</span>}
          </div>

          <div className="form-actions">
            <button 
              type="submit" 
              className="btn-submit"
              disabled={loading || !phoneNumber}
            >
              {loading ? 'Updating...' : 'Submit'}
            </button>
          </div>

          <p className="help-text">
            Your phone number will be visible to mentors for project coordination.
          </p>
        </form>
      </div>
    </div>
  );
};

export default PhoneNumberModal;
