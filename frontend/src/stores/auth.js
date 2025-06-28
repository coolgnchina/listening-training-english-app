import { defineStore } from 'pinia';
import { jwtDecode } from 'jwt-decode';
import { buildApiUrl } from '../config/api';

// 修复重复导入问题

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    userId: (state) => (state.user ? state.user.user_id : null),
    username: (state) => (state.user ? state.user.username : null),
    isVip: (state) => (state.user ? state.user.is_vip : false),
    isAdmin: (state) => state.user?.is_admin || false,
  },
  actions: {
    async login(username, password) {
      try {
        const response = await fetch(buildApiUrl('/api/login'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username, password }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Login failed');
        }

        const data = await response.json();
        this.token = data.token;
        localStorage.setItem('token', data.token);
        
        const decodedToken = jwtDecode(data.token);
        this.user = { 
          user_id: decodedToken.user_id, 
          username: decodedToken.username || username,
          is_vip: decodedToken.is_vip, 
          is_admin: decodedToken.is_admin 
        };
        localStorage.setItem('user', JSON.stringify(this.user));

        return true;
      } catch (error) {
        console.error('Login error:', error);
        return false;
      }
    },
    async register(username, password) {
      try {
        const response = await fetch(buildApiUrl('/api/register'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username, password }),
        });
  
        const data = await response.json();
        
        if (!response.ok) {
          return {
            success: false,
            message: data.error || 'Registration failed'
          };
        }

        return {
          success: true,
          message: data.message
        };
      } catch (error) {
        console.error('Registration error:', error);
        return {
          success: false,
          message: 'Network error occurred'
        };
      }
    },

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    },
    fetchUser() {
      const token = localStorage.getItem('token');
      if (token) {
        const decodedToken = jwtDecode(token);
        this.user = { user_id: decodedToken.user_id, is_vip: decodedToken.is_vip, is_admin: decodedToken.is_admin };
        localStorage.setItem('user', JSON.stringify(this.user));
      } else {
        this.user = null;
        localStorage.removeItem('user');
      }
    }
  },
});