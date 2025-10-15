<template>
  <div class="inventory-page">
    <div class="container">
      <div class="page-header">
        <div class="header-left">
          <h1>Inventory Management</h1>
          <p class="page-description">Monitor and manage stock levels across all stores</p>
        </div>
        <div class="header-right">
          <button class="btn btn-secondary" @click="handleExport">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Export
          </button>
          <button class="btn btn-primary" @click="handleUpdateInventory">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="23 4 23 10 17 10"/>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
            Refresh
          </button>
        </div>
      </div>

      <!-- AI Agent Alert Banner -->
      <div v-if="summary && summary.lowStockCount > 0" class="ai-banner">
        <div class="banner-icon">🤖</div>
        <div class="banner-content">
          <div class="banner-title">
            <strong>{{ summary.lowStockCount }}</strong> items are low on stock!
          </div>
          <div class="banner-text">
            Our AI Agent can help you prioritize restocking and optimize inventory levels across all stores.
          </div>
        </div>
        <router-link to="/management/ai-agent" class="banner-button">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4"/>
            <path d="M12 8h.01"/>
          </svg>
          Launch AI Agent
        </router-link>
      </div>

      <!-- Summary Cards -->
      <div v-if="summary" class="summary-cards">
        <div class="summary-card">
          <div class="card-icon">📦</div>
          <div class="card-content">
            <div class="card-label">Total Items</div>
            <div class="card-value">{{ summary.totalItems }}</div>
          </div>
        </div>
        <div class="summary-card alert">
          <div class="card-icon">⚠️</div>
          <div class="card-content">
            <div class="card-label">Low Stock</div>
            <div class="card-value">{{ summary.lowStockCount }}</div>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">💰</div>
          <div class="card-content">
            <div class="card-label">Stock Value</div>
            <div class="card-value">${{ formatNumber(summary.totalStockValue) }}</div>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">🏪</div>
          <div class="card-content">
            <div class="card-label">Retail Value</div>
            <div class="card-value">${{ formatNumber(summary.totalRetailValue) }}</div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-bar">
        <div class="filter-group">
          <label>Store</label>
          <select v-model="filters.storeId" @change="loadInventory">
            <option :value="null">All Stores</option>
            <option v-for="store in stores" :key="store.id" :value="store.id">
              {{ store.name }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <label>Category</label>
          <select v-model="filters.category" @change="loadInventory">
            <option :value="null">All Categories</option>
            <option v-for="cat in categories" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <label>
            <input type="checkbox" v-model="filters.lowStockOnly" @change="loadInventory" />
            Show Low Stock Only
          </label>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading inventory...</p>
      </div>

      <!-- Inventory Table -->
      <div v-else-if="inventory.length > 0" class="inventory-table-container">
        <table class="inventory-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>SKU</th>
              <th>Store</th>
              <th>Category</th>
              <th>Stock Level</th>
              <th>Reorder Point</th>
              <th>Status</th>
              <th>Stock Value</th>
              <th>Retail Value</th>
              <th>Supplier</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in inventory" :key="`${item.storeId}-${item.productId}`" 
                :class="{ 'low-stock-row': item.isLowStock }">
              <td class="product-cell">
                <div class="product-info">
                  <img v-if="item.imageUrl" :src="`/images/${item.imageUrl}`" 
                       :alt="item.productName" class="product-thumb" 
                       @error="handleImageError" />
                  <div class="product-thumb-placeholder" v-else>📦</div>
                  <div class="product-details">
                    <div class="product-name">{{ item.productName }}</div>
                    <div class="product-type">{{ item.type }}</div>
                  </div>
                </div>
              </td>
              <td class="sku-cell">{{ item.sku }}</td>
              <td>
                <div class="store-info">
                  <div class="store-name">{{ item.storeName }}</div>
                  <div class="store-location">{{ item.storeLocation }}</div>
                </div>
              </td>
              <td>
                <span class="category-badge">{{ item.category }}</span>
              </td>
              <td class="stock-level">
                <strong>{{ item.stockLevel }}</strong> units
              </td>
              <td class="reorder-point">{{ item.reorderPoint }}</td>
              <td>
                <span v-if="item.isLowStock" class="status-badge status-low">
                  ⚠️ Low Stock
                </span>
                <span v-else class="status-badge status-good">
                  ✓ Good
                </span>
              </td>
              <td class="value-cell">${{ formatNumber(item.stockValue) }}</td>
              <td class="value-cell">${{ formatNumber(item.retailValue) }}</td>
              <td>
                <div v-if="item.supplierName" class="supplier-info">
                  <div class="supplier-name">{{ item.supplierName }}</div>
                  <div class="supplier-code">{{ item.supplierCode }}</div>
                  <div class="lead-time">Lead: {{ item.leadTime }}d</div>
                </div>
                <span v-else class="no-supplier">No supplier</span>
              </td>
              <td class="actions-cell">
                <button class="btn-icon" @click="handleAdjustStock(item)" title="Adjust Stock">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                </button>
                <button class="btn-icon" @click="handleReorder(item)" title="Reorder">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="9" cy="21" r="1"/>
                    <circle cx="20" cy="21" r="1"/>
                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M20 7h-9"/>
          <path d="M14 17H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10"/>
          <path d="M18 12h4"/>
          <path d="M18 17h4"/>
        </svg>
        <h3>No inventory items found</h3>
        <p>Try adjusting your filters or check back later.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { managementService } from '../../services/management';

export default {
  name: 'InventoryPage',
  data() {
    return {
      loading: false,
      inventory: [],
      summary: null,
      filters: {
        storeId: null,
        category: null,
        lowStockOnly: false
      },
      stores: [
        { id: 1, name: 'Zava Online Store' },
        { id: 2, name: 'Zava Pop-Up Bellevue Square' },
        { id: 3, name: 'Zava Pop-Up Everett Station' },
        { id: 4, name: 'Zava Pop-Up Kirkland Waterfront' },
        { id: 5, name: 'Zava Pop-Up Pike Place' },
        { id: 6, name: 'Zava Pop-Up Redmond Town Center' },
        { id: 7, name: 'Zava Pop-Up Spokane Pavilion' },
        { id: 8, name: 'Zava Pop-Up Tacoma Mall' }
      ],
      categories: [
        'Accessories',
        'Apparel - Bottoms',
        'Apparel - Tops',
        'Eyewear',
        'Footwear',
        'Outerwear'
      ]
    };
  },
  async mounted() {
    await this.loadInventory();
  },
  methods: {
    async loadInventory() {
      this.loading = true;
      try {
        const params = {
          limit: 100
        };
        
        if (this.filters.storeId) {
          params.store_id = this.filters.storeId;
        }
        if (this.filters.category) {
          params.category = this.filters.category;
        }
        if (this.filters.lowStockOnly) {
          params.low_stock_only = true;
        }

        const data = await managementService.getInventory(params);
        this.inventory = data.inventory || [];
        this.summary = data.summary || null;
      } catch (error) {
        console.error('Error loading inventory:', error);
      } finally {
        this.loading = false;
      }
    },
    formatNumber(num) {
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(num);
    },
    handleImageError(event) {
      event.target.style.display = 'none';
      event.target.nextElementSibling.style.display = 'flex';
    },
    handleUpdateInventory() {
      this.loadInventory();
    },
    handleExport() {
      alert('Export inventory to CSV - Coming soon!');
    },
    handleAdjustStock(item) {
      alert(`Adjust stock for ${item.productName} at ${item.storeName} - Coming soon!`);
    },
    handleReorder(item) {
      alert(`Create reorder request for ${item.productName} from ${item.supplierName} - Coming soon!`);
    }
  }
};
</script>

<style scoped>
.inventory-page {
  padding-bottom: 2rem;
}

.inventory-page .container {
  max-width: 100%;
  padding: 0 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header-left h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
}

.page-description {
  color: var(--secondary-color);
  font-size: 0.95rem;
}

.header-right {
  display: flex;
  gap: 0.75rem;
}

.header-right .btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* AI Agent Banner */
.ai-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 2rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.banner-icon {
  font-size: 3rem;
  line-height: 1;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.banner-content {
  flex: 1;
}

.banner-title {
  font-size: 1.125rem;
  margin-bottom: 0.5rem;
}

.banner-title strong {
  font-size: 1.25rem;
  font-weight: 700;
}

.banner-text {
  font-size: 0.9rem;
  opacity: 0.95;
  line-height: 1.5;
}

.banner-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  color: #667eea;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.banner-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background: #f8f9ff;
}

.banner-button svg {
  stroke: #667eea;
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.summary-card.alert {
  border-left: 4px solid #d73a49;
}

.card-icon {
  font-size: 2rem;
  line-height: 1;
}

.card-content {
  flex: 1;
}

.card-label {
  font-size: 0.875rem;
  color: var(--secondary-color);
  margin-bottom: 0.25rem;
}

.card-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--primary-color);
}

/* Filters */
.filters-bar {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
  display: flex;
  gap: 1.5rem;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group select {
  padding: 0.5rem 1rem;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  font-size: 0.875rem;
  min-width: 200px;
  background: white;
}

.filter-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* Loading */
.loading {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.spinner {
  border: 3px solid #f3f4f6;
  border-top: 3px solid var(--accent-color);
  border-radius: 50%;
  width: 48px;
  height: 48px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Inventory Table */
.inventory-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow-x: auto;
  overflow-y: visible;
}

.inventory-table {
  width: 100%;
  min-width: 1200px;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.inventory-table thead {
  background: #f6f8fa;
  border-bottom: 2px solid #d0d7de;
}

.inventory-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--primary-color);
  white-space: nowrap;
}

.inventory-table td {
  padding: 1rem;
  border-bottom: 1px solid #d0d7de;
  vertical-align: middle;
}

.inventory-table tbody tr {
  transition: background-color 0.2s;
}

.inventory-table tbody tr:hover {
  background-color: #f6f8fa;
}

.low-stock-row {
  background-color: #fff8e6;
}

.low-stock-row:hover {
  background-color: #fff3d4;
}

/* Product Cell */
.product-cell {
  min-width: 250px;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.product-thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #d0d7de;
}

.product-thumb-placeholder {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f8fa;
  border-radius: 6px;
  border: 1px solid #d0d7de;
  font-size: 1.5rem;
}

.product-details {
  flex: 1;
}

.product-name {
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 0.25rem;
}

.product-type {
  font-size: 0.75rem;
  color: var(--secondary-color);
}

.sku-cell {
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 0.8rem;
  color: #6a737d;
}

/* Store Info */
.store-info {
  min-width: 150px;
}

.store-name {
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 0.25rem;
}

.store-location {
  font-size: 0.75rem;
  color: var(--secondary-color);
}

/* Category Badge */
.category-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #e1e4e8;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary-color);
  white-space: nowrap;
}

/* Stock Level */
.stock-level {
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  min-width: 100px;
}

.reorder-point {
  color: var(--secondary-color);
  text-align: center;
  min-width: 80px;
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
  min-width: 90px;
  justify-content: center;
}

.status-good {
  background: #d4edda;
  color: #155724;
}

.status-low {
  background: #fff3cd;
  color: #856404;
}

/* Value Cells */
.value-cell {
  text-align: right;
  font-weight: 600;
  color: var(--primary-color);
  white-space: nowrap;
  min-width: 110px;
  padding-right: 1.5rem !important;
}

/* Supplier Info */
.supplier-info {
  min-width: 160px;
}

.supplier-name {
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 0.25rem;
  font-size: 0.8rem;
}

.supplier-code {
  font-size: 0.7rem;
  color: var(--secondary-color);
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  margin-bottom: 0.25rem;
}

.lead-time {
  font-size: 0.7rem;
  color: var(--secondary-color);
}

.no-supplier {
  color: var(--secondary-color);
  font-style: italic;
  font-size: 0.8rem;
}

/* Actions */
.actions-cell {
  white-space: nowrap;
  min-width: 100px;
}

.btn-icon {
  background: transparent;
  border: 1px solid #d0d7de;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 0.5rem;
}

.btn-icon:hover {
  background: #f6f8fa;
  border-color: var(--accent-color);
}

.btn-icon svg {
  display: block;
  stroke: var(--primary-color);
}

.btn-icon:hover svg {
  stroke: var(--accent-color);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.empty-state svg {
  stroke: var(--secondary-color);
  margin-bottom: 1.5rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--secondary-color);
}

/* Responsive */
@media (max-width: 1600px) {
  .inventory-table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}

@media (max-width: 1200px) {
  .inventory-table {
    font-size: 0.8rem;
  }
  
  .inventory-table th,
  .inventory-table td {
    padding: 0.75rem 0.5rem;
  }
}

@media (max-width: 768px) {
  .inventory-page .container {
    padding: 0 1rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr 1fr;
  }
  
  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group select {
    min-width: 100%;
  }
  
  .header-right {
    flex-wrap: wrap;
  }
  
  .ai-banner {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }
  
  .banner-icon {
    font-size: 2.5rem;
  }
  
  .banner-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
