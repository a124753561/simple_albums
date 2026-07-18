import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_ROUTER_BASE),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomePage.vue') },
    { path: '/albums', name: 'albums', component: () => import('@/views/AlbumListPage.vue') },
    { path: '/albums/:id', name: 'album-detail', component: () => import('@/views/AlbumDetailPage.vue') },
    { path: '/contact', name: 'contact', component: () => import('@/views/ContactPage.vue') },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
