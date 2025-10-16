import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8091';

export const config = {
  apiBaseUrl: API_BASE_URL,
  wsBaseUrl: API_BASE_URL.replace(/^http[s]/, 'ws'),
  
  // Timeout for all API requests (in milliseconds)
  timeout: 3000, // 3 seconds
  
  endpoints: {
    categories: `${API_BASE_URL}/api/categories`,
    products: `${API_BASE_URL}/api/products`,
    productsByCategory: (category) => `${API_BASE_URL}/api/products/category/${encodeURIComponent(category)}`,
    featuredProducts: `${API_BASE_URL}/api/products/featured`,
    stores: `${API_BASE_URL}/api/stores`,
  },
  // Placeholder for product images - you'll add these later
  getProductImageUrl: (productId) => `/images/products/${productId}.jpg`,
  placeholderImage: '/images/placeholder.png'
};

// Create a pre-configured axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: config.timeout,
  headers: {
    'Content-Type': 'application/json'
  }
});
