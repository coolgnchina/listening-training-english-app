import { defineStore } from 'pinia';
import { jwtDecode } from 'jwt-decode';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    userId: (state) => (state.user ? state.user.user_id : null),
  },
  actions: {
    async login(username, password) {
      try {
        const response = await fetch('http://127.0.0.1:5000/login', {
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
        this.user = { user_id: decodedToken.user_id };
        localStorage.setItem('user', JSON.stringify(this.user));

        return true;
      } catch (error) {
        console.error('Login error:', error);
        return false;
      }
    },
    async register(username, password) {
        try {
          const response = await fetch('http://127.0.0.1:5000/register', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
          });
  
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Registration failed');
          }
  
          return true;
        } catch (error) {
          console.error('Registration error:', error);
          return false;
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
        this.user = { user_id: decodedToken.user_id };
        localStorage.setItem('user', JSON.stringify(this.user));
      } else {
        this.user = null;
        localStorage.removeItem('user');
      }
    }
  },
});