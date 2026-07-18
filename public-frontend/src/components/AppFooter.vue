<template>
  <footer class="footer">
    <p>© {{ year }} 相册系统. All rights reserved.</p>
  </footer>
</template>

<script setup lang="ts">
const year = new Date().getFullYear()
</script>

<style scoped>
.footer { text-align: center; padding: 24px 16px; color: #999; font-size: 13px; }
</style>
