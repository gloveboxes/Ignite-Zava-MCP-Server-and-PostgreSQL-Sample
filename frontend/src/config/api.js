const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8091';

export const config = {
  apiBaseUrl: API_BASE_URL,
  endpoints: {
    categories: `${API_BASE_URL}/api/categories`,
    products: `${API_BASE_URL}/api/products`,
    productsByCategory: (category) => `${API_BASE_URL}/api/products/category/${encodeURIComponent(category)}`,
    featuredProducts: `${API_BASE_URL}/api/products/featured`,
  },
  // Placeholder for product images - you'll add these later
  getProductImageUrl: (productId) => `/images/products/${productId}.jpg`,
  placeholderImage: '/images/placeholder.png'
};
