<template>
  <header class="header">
    <div class="header-inner">
      <router-link to="/" class="logo">📷 相册</router-link>
      <nav class="nav-desktop">
        <router-link to="/" :class="{ active: $route.path === '/' }">首页</router-link>
        <router-link to="/albums" :class="{ active: $route.path.startsWith('/albums') }">相册</router-link>
        <router-link to="/contact" :class="{ active: $route.path === '/contact' }">联系档案</router-link>
      </nav>
      <button class="menu-btn" @click="mobileMenu = !mobileMenu">☰</button>
    </div>
    <div v-show="mobileMenu" class="nav-mobile">
      <router-link to="/" @click="mobileMenu = false">首页</router-link>
      <router-link to="/albums" @click="mobileMenu = false">相册</router-link>
      <router-link to="/contact" @click="mobileMenu = false">联系档案</router-link>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const mobileMenu = ref(false)
</script>

<style scoped>
.header { position: fixed; top: 0; left: 0; right: 0; z-index: 100; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,.1); }
.header-inner { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 48px; padding: 0 16px; }
.logo { font-size: 20px; font-weight: bold; color: #333; text-decoration: none; }
.nav-desktop { display: flex; gap: 24px; }
.nav-desktop a { color: #555; text-decoration: none; font-size: 15px; }
.nav-desktop a.active, .nav-desktop a:hover { color: #1989fa; }
.menu-btn { display: none; background: none; border: none; font-size: 24px; cursor: pointer; }
.nav-mobile { display: none; background: #fff; padding: 8px 16px; border-top: 1px solid #eee; }
.nav-mobile a { display: block; padding: 10px 0; color: #555; text-decoration: none; border-bottom: 1px solid #f5f5f5; }
@media (max-width: 768px) {
  .nav-desktop { display: none; }
  .menu-btn { display: block; }
  .nav-mobile { display: block; }
}
</style>
