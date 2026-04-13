// src/utils/auth.js
// Centralized authentication utilities

/**
 * Clear a specific cookie by name
 */
const clearCookie = (name) => {
  // Clear for current domain
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
  
  // Clear for parent domain (tech-iitb.org)
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=.tech-iitb.org;`;
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=tech-iitb.org;`;
  
  // Clear for specific subdomain
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=.socb.tech-iitb.org;`;
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=socb.tech-iitb.org;`;
};

/**
 * Clear all authentication and user data from localStorage AND cookies
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
  
  // Clear all auth-related cookies
  clearCookie('auth');
  clearCookie('csrftoken');
  clearCookie('sessionid');
  
  console.log('[AUTH] Cleared all authentication data from localStorage and cookies');
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
    console.log('[AUTH] Token:', token.substring(0, 20) + '...');
    console.log('[AUTH] Memberships:', memberships?.length || 0);
    console.log('[AUTH] Is Manager:', isManager);
    return true;
  } catch (error) {
    console.error('[AUTH] Error saving auth data:', error);
    clearAuthData(); // Clean up on error
    return false;
  }
};
