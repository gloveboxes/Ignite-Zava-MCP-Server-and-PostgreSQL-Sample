<template>
  <div class="inventory-page">
    <div class="container">
      <div class="page-header">
        <div class="header-left">
          <h1>Inventory Management</h1>
          <p class="page-description">Monitor and manage stock levels across all stores</p>
        </div>
        <div class="header-right">
          <button class="btn btn-primary" @click="handleUpdateInventory">
            Update Inventory
          </button>
        </div>
      </div>

      <!-- Coming in next message: Full inventory table implementation -->
      <div class="coming-soon">
        <p>Inventory management interface with tables showing:</p>
        <ul>
          <li>Stock levels per store</li>
          <li>Low stock alerts</li>
          <li>Reorder points</li>
          <li>Total inventory value</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InventoryPage',
  methods: {
    handleUpdateInventory() {
      alert('Update Inventory - Coming soon!');
    }
  }
};
</script>

<style scoped>
.inventory-page {
  padding-bottom: 2rem;
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
}

.coming-soon {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
</style>
