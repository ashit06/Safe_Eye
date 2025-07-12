// src/lib/auth.ts

// Helper function to set cookies (client-side only)
export const setCookie = (name: string, value: string, days: number = 7) => {
  if (typeof window === 'undefined') return; // no-op on server
  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
};

// Helper function to get token from multiple sources
export const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  // Try localStorage first
  let token = localStorage.getItem('accessToken');

  // If not in localStorage, try cookies
  if (!token && typeof document !== 'undefined') {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'accessToken') {
        token = value;
        break;
      }
    }
  }

  return token;
};

// Helper function to clear all auth data
export const clearAuthData = (): void => {
  if (typeof window === 'undefined') return;

  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');

  if (typeof document !== 'undefined') {
    // Clear cookies
    document.cookie = 'accessToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    document.cookie = 'refreshToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  }
};

// Helper function to store auth tokens
export const storeAuthTokens = (access: string, refresh: string): void => {
  if (typeof window === 'undefined') return;

  // Store tokens in both localStorage and cookies for cross-browser compatibility
  localStorage.setItem('accessToken', access);
  localStorage.setItem('refreshToken', refresh);

  // Also store in cookies for middleware compatibility
  setCookie('accessToken', access, 1); // 1 day expiry
  setCookie('refreshToken', refresh, 7); // 7 days expiry
};

// Helper function to check if user is authenticated
export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};
