import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_ROUTER_BASE),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/login/LoginPage.vue'),
      meta: { noAuth: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/AdminLayout.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardPage.vue'),
          meta: { title: '仪表盘' },
        },
        {
          path: 'users',
          name: 'users',
          component: () => import('@/views/users/UserListPage.vue'),
          meta: { title: '用户管理' },
        },
        {
          path: 'categories',
          name: 'categories',
          component: () => import('@/views/categories/CategoryPage.vue'),
          meta: { title: '分类管理' },
        },
        {
          path: 'albums',
          name: 'albums',
          component: () => import('@/views/albums/AlbumListPage.vue'),
          meta: { title: '相册管理' },
        },
        {
          path: 'albums/:id/photos',
          name: 'album-photos',
          component: () => import('@/views/albums/AlbumDetailPage.vue'),
          meta: { title: '图片管理' },
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/settings/SettingsPage.vue'),
          meta: { title: '系统设置' },
        },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.meta.noAuth) {
    if (authStore.isLoggedIn) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    if (!authStore.isLoggedIn) {
      next('/login')
    } else {
      next()
    }
  }
})

export default router
