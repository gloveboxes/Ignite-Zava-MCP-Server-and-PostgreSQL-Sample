// Store for authentication state
import { reactive } from 'vue';

export const authStore = reactive({
  isAuthenticated: false,
  user: null,
  
  login(username, password) {
    // Simple authentication check
    if (username === 'admin' && password === 'zava') {
      this.isAuthenticated = true;
      this.user = {
        username: 'admin',
        role: 'Store Manager',
        name: 'Admin User'
      };
      // Store in sessionStorage
      sessionStorage.setItem('auth', JSON.stringify(this.user));
      return true;
    }
    return false;
  },
  
  logout() {
    this.isAuthenticated = false;
    this.user = null;
    sessionStorage.removeItem('auth');
  },
  
  checkAuth() {
    const stored = sessionStorage.getItem('auth');
    if (stored) {
      this.user = JSON.parse(stored);
      this.isAuthenticated = true;
    }
  }
});
