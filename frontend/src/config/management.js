const MANAGEMENT_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8091';

export const managementConfig = {
  apiBaseUrl: MANAGEMENT_API_BASE_URL,
  endpoints: {
    suppliers: `${MANAGEMENT_API_BASE_URL}/api/management/suppliers`,
    inventory: `${MANAGEMENT_API_BASE_URL}/api/management/inventory`,
    products: `${MANAGEMENT_API_BASE_URL}/api/management/products`,
    policies: `${MANAGEMENT_API_BASE_URL}/api/management/policies`,
    dashboard: `${MANAGEMENT_API_BASE_URL}/api/management/dashboard`,
  }
};
