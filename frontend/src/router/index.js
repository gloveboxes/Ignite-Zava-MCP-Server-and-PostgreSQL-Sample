import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import CategoryPage from '../views/CategoryPage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/category/:category',
    name: 'Category',
    component: CategoryPage
  },
  {
    path: '/category/:category/:subcategory',
    name: 'Subcategory',
    component: CategoryPage
  },
  {
    path: '/stores',
    name: 'Stores',
    component: () => import('../views/StoresPage.vue')
  },
  {
    path: '/product/:id',
    name: 'Product',
    component: () => import('../views/ProductPage.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

export default router;
