// src/utils/auth.js
// Centralized authentication utilities

/**
 * Clear all authentication and user data from localStorage
 * Use this function whenever logging out or when authentication fails
 */
export const clearAuthData = () => {
  const keysToRemove = [
    'authToken',
    'role',
    'memberships',
    'is_manager',
    'accessid',
  ];
  
  keysToRemove.forEach(key => {
    localStorage.removeItem(key);
  });
  
  console.log('[AUTH] Cleared all authentication data from localStorage');
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  const token = localStorage.getItem('authToken');
  return !!token;
};

/**
 * Get user memberships from localStorage
 */
export const getMemberships = () => {
  try {
    const memberships = localStorage.getItem('memberships');
    return memberships ? JSON.parse(memberships) : [];
  } catch (error) {
    console.error('[AUTH] Error parsing memberships:', error);
    return [];
  }
};

/**
 * Check if user is a manager
 */
export const isManager = () => {
  return localStorage.getItem('is_manager') === 'true';
};

/**
 * Get auth token
 */
export const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

/**
 * Save authentication data after successful login
 * Only call this after verifying the login was successful
 */
export const saveAuthData = (token, memberships, isManager) => {
  if (!token) {
    console.error('[AUTH] Cannot save auth data: token is missing');
    return false;
  }
  
  try {
    localStorage.setItem('authToken', token);
    localStorage.setItem('memberships', JSON.stringify(memberships || []));
    localStorage.setItem('is_manager', isManager ? 'true' : 'false');
    
    // Legacy role fallback for components that still read localStorage.role
    const approvedMembership = memberships?.find((m) => m.is_approved);
    localStorage.setItem('role', approvedMembership?.role || 'mentee');
    
    console.log('[AUTH] Saved authentication data to localStorage');
    return true;
  } catch (error) {
    console.error('[AUTH] Error saving auth data:', error);
    clearAuthData(); // Clean up on error
    return false;
  }
};
