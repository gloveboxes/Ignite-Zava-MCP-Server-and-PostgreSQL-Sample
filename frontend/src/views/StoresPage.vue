<template>
  <div class="stores-page">
    <div class="container">
      <h1 class="page-title">Our Popup Store Locations</h1>
      <p class="page-subtitle">Visit us at any of our 7 locations across Washington State</p>

      <div class="stores-grid">
        <div v-for="store in stores" :key="store.id" class="store-card">
          <div class="store-header">
            <h3 class="store-name">{{ store.name }}</h3>
            <span class="store-badge" :class="store.status">{{ store.status }}</span>
          </div>
          <div class="store-details">
            <div class="detail-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
              <span>{{ store.location }}</span>
            </div>
            <div class="detail-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
              <span>{{ store.hours }}</span>
            </div>
            <div class="detail-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
              <span>{{ store.products }} products in stock</span>
            </div>
          </div>
          <button class="btn btn-outline store-btn" @click="handleDirections(store)">
            Get Directions
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StoresPage',
  data() {
    return {
      stores: [
        {
          id: 1,
          name: 'Zava Pop-Up Pike Place',
          location: 'Pike Place Market, Seattle, WA',
          hours: 'Mon-Sun: 9am-8pm',
          products: 52,
          status: 'Open',
          inventory: '$48,910'
        },
        {
          id: 2,
          name: 'Zava Pop-Up Bellevue Square',
          location: 'Bellevue Square Mall, Bellevue, WA',
          hours: 'Mon-Sat: 10am-9pm, Sun: 11am-7pm',
          products: 47,
          status: 'Open',
          inventory: '$43,258'
        },
        {
          id: 3,
          name: 'Zava Pop-Up Kirkland Waterfront',
          location: 'Kirkland Waterfront, Kirkland, WA',
          hours: 'Mon-Sun: 10am-7pm',
          products: 54,
          status: 'Open',
          inventory: '$34,411'
        },
        {
          id: 4,
          name: 'Zava Pop-Up Tacoma Mall',
          location: 'Tacoma Mall, Tacoma, WA',
          hours: 'Mon-Sat: 10am-9pm, Sun: 11am-6pm',
          products: 50,
          status: 'Open',
          inventory: '$39,531'
        },
        {
          id: 5,
          name: 'Zava Pop-Up Spokane Pavilion',
          location: 'Spokane Pavilion, Spokane, WA',
          hours: 'Mon-Sun: 10am-8pm',
          products: 52,
          status: 'Open',
          inventory: '$32,889'
        },
        {
          id: 6,
          name: 'Zava Pop-Up Everett Station',
          location: 'Everett Station Square, Everett, WA',
          hours: 'Mon-Sat: 10am-8pm, Sun: 11am-6pm',
          products: 47,
          status: 'Open',
          inventory: '$28,652'
        },
        {
          id: 7,
          name: 'Zava Pop-Up Redmond Town Center',
          location: 'Redmond Town Center, Redmond, WA',
          hours: 'Mon-Sun: 10am-7pm',
          products: 45,
          status: 'Open',
          inventory: '$21,807'
        }
      ]
    };
  },
  methods: {
    handleDirections(store) {
      alert(`Directions to ${store.name} - Coming soon!`);
    }
  }
};
</script>

<style scoped>
.stores-page {
  min-height: 100vh;
  padding: 3rem 0;
}

.page-title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: var(--primary-color);
}

.page-subtitle {
  text-align: center;
  font-size: 1.125rem;
  color: var(--secondary-color);
  margin-bottom: 3rem;
}

.stores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
}

.store-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 2rem;
  transition: all 0.3s;
}

.store-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
}

.store-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.store-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--primary-color);
  flex: 1;
}

.store-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.store-badge.Open {
  background: #d4edda;
  color: #155724;
}

.store-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-color);
  font-size: 0.9rem;
}

.detail-item svg {
  flex-shrink: 0;
  color: var(--accent-color);
}

.store-btn {
  width: 100%;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .stores-grid {
    grid-template-columns: 1fr;
  }
}
</style>
