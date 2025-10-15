<template>
  <div class="dashboard-page">
    <div class="container">
      <div class="page-header">
        <h1>Dashboard</h1>
        <p class="page-description">Overview of store operations and key metrics</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>

      <!-- Dashboard Content -->
      <div v-else>
        <!-- Stats Cards -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon revenue">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">${{ formatNumber(stats.totalRevenue) }}</div>
              <div class="stat-label">Total Inventory Value</div>
              <div class="stat-change positive">+{{ stats.revenueChange }}% from last month</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon products">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
                <line x1="3" y1="6" x2="21" y2="6"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalProducts }}</div>
              <div class="stat-label">Total Products</div>
              <div class="stat-info">Across all categories</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon suppliers">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="8.5" cy="7" r="4"/>
                <path d="M20 8v6M23 11h-6"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalSuppliers }}</div>
              <div class="stat-label">Active Suppliers</div>
              <div class="stat-info">{{ Math.round(stats.totalSuppliers * 0.8) }} ESG compliant</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon stores">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalStores }}</div>
              <div class="stat-label">Popup Stores</div>
              <div class="stat-info">Across Washington State</div>
            </div>
          </div>
        </div>

        <!-- Alerts -->
        <div class="alerts-section">
          <div class="alert alert-warning">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <div>
              <strong>{{ stats.lowStockItems }} products</strong> are running low on stock
              <router-link to="/management/inventory" class="alert-link">View Inventory →</router-link>
            </div>
          </div>

          <div class="alert alert-info">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
            <div>
              <strong>{{ stats.pendingOrders }} pending orders</strong> awaiting approval
            </div>
          </div>
        </div>

        <!-- Charts Row -->
        <div class="charts-row">
          <!-- Top Categories Chart -->
          <div class="chart-card">
            <h3 class="chart-title">Top Categories by Revenue</h3>
            <div class="category-chart">
              <div 
                v-for="category in stats.topCategories" 
                :key="category.name"
                class="category-bar"
              >
                <div class="category-info">
                  <span class="category-name">{{ category.name }}</span>
                  <span class="category-revenue">${{ formatNumber(category.revenue) }}</span>
                </div>
                <div class="bar-container">
                  <div class="bar-fill" :style="{ width: category.percentage + '%' }"></div>
                  <span class="bar-percentage">{{ category.percentage }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Activity -->
          <div class="chart-card">
            <h3 class="chart-title">Recent Activity</h3>
            <div class="activity-list">
              <div 
                v-for="activity in stats.recentActivity" 
                :key="activity.id"
                class="activity-item"
              >
                <div class="activity-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                </div>
                <div class="activity-content">
                  <div class="activity-action">{{ activity.action }}</div>
                  <div class="activity-details">
                    {{ activity.item }}
                    <span v-if="activity.store"> • {{ activity.store }}</span>
                  </div>
                  <div class="activity-time">{{ activity.time }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
          <h3>Quick Actions</h3>
          <div class="actions-grid">
            <router-link to="/management/suppliers" class="action-card">
              <div class="action-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="8.5" cy="7" r="4"/>
                  <path d="M20 8v6M23 11h-6"/>
                </svg>
              </div>
              <div class="action-content">
                <h4>Add Supplier</h4>
                <p>Register a new supplier</p>
              </div>
            </router-link>

            <router-link to="/management/inventory" class="action-card">
              <div class="action-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                </svg>
              </div>
              <div class="action-content">
                <h4>Update Inventory</h4>
                <p>Manage stock levels</p>
              </div>
            </router-link>

            <router-link to="/management/products" class="action-card">
              <div class="action-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
                  <line x1="3" y1="6" x2="21" y2="6"/>
                </svg>
              </div>
              <div class="action-content">
                <h4>Add Product</h4>
                <p>Create new product listing</p>
              </div>
            </router-link>

            <router-link to="/management/policies" class="action-card">
              <div class="action-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <div class="action-content">
                <h4>Review Policies</h4>
                <p>View company policies</p>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { managementService } from '../services/management';

export default {
  name: 'DashboardPage',
  data() {
    return {
      loading: false,
      stats: {
        totalRevenue: 0,
        totalProducts: 0,
        totalSuppliers: 0,
        totalStores: 0,
        lowStockItems: 0,
        pendingOrders: 0,
        revenueChange: 0,
        topCategories: [],
        recentActivity: []
      }
    };
  },
  async mounted() {
    await this.loadDashboard();
  },
  methods: {
    async loadDashboard() {
      this.loading = true;
      try {
        this.stats = await managementService.getDashboardStats();
      } catch (error) {
        console.error('Error loading dashboard:', error);
      } finally {
        this.loading = false;
      }
    },
    formatNumber(num) {
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(num);
    }
  }
};
</script>

<style scoped>
.dashboard-page {
  padding-bottom: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
}

.page-description {
  color: var(--secondary-color);
  font-size: 1rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon.revenue { background: #e3f2fd; color: #1976d2; }
.stat-icon.products { background: #f3e5f5; color: #7b1fa2; }
.stat-icon.suppliers { background: #e8f5e9; color: #388e3c; }
.stat-icon.stores { background: #fff3e0; color: #f57c00; }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--secondary-color);
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.stat-change {
  font-size: 0.75rem;
  font-weight: 600;
}

.stat-change.positive { color: #388e3c; }

.stat-info {
  font-size: 0.75rem;
  color: var(--secondary-color);
}

/* Alerts */
.alerts-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.alert {
  flex: 1;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  font-size: 0.9rem;
}

.alert svg {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.alert-warning {
  background: #fff3cd;
  border: 1px solid #ffc107;
  color: #856404;
}

.alert-info {
  background: #d1ecf1;
  border: 1px solid #17a2b8;
  color: #0c5460;
}

.alert-link {
  color: inherit;
  font-weight: 600;
  text-decoration: underline;
  margin-left: 0.5rem;
}

/* Charts */
.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--primary-color);
}

/* Category Chart */
.category-chart {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.category-bar {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.category-name {
  font-weight: 600;
  color: var(--text-color);
}

.category-revenue {
  color: var(--secondary-color);
  font-weight: 500;
}

.bar-container {
  position: relative;
  height: 24px;
  background: var(--hover-color);
  border-radius: 12px;
  overflow: hidden;
}

.bar-fill {
  position: absolute;
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 12px;
  transition: width 0.6s ease;
}

.bar-percentage {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-color);
}

/* Activity List */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  gap: 0.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.activity-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--hover-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-color);
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-action {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.activity-details {
  font-size: 0.875rem;
  color: var(--secondary-color);
  margin-bottom: 0.25rem;
}

.activity-time {
  font-size: 0.75rem;
  color: var(--secondary-color);
}

/* Quick Actions */
.quick-actions {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.quick-actions h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--primary-color);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  transition: all 0.2s;
}

.action-card:hover {
  border-color: var(--accent-color);
  background: var(--hover-color);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: var(--hover-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-color);
  flex-shrink: 0;
}

.action-content h4 {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: var(--text-color);
}

.action-content p {
  font-size: 0.75rem;
  color: var(--secondary-color);
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .alerts-section {
    flex-direction: column;
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
