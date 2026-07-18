<template>
  <div>
    <div class="album-grid">
      <div v-for="album in albums" :key="album.id" class="album-card" @click="$router.push(`/albums/${album.id}`)">
        <div class="cover-wrapper">
          <img v-if="album.cover" :src="album.cover" :alt="album.title" />
          <div v-else class="placeholder">暂无封面</div>
        </div>
        <div class="info">
          <p class="title">{{ album.title }}</p>
          <p class="count">{{ album.photo_count }} 张</p>
        </div>
      </div>
    </div>
    <div class="loading-row" v-if="loading">
      <van-loading size="24" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ albums: any[]; loading?: boolean }>()
</script>

<style scoped>
.album-grid {
  display: grid; gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}
@media (max-width: 768px) {
  .album-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
}
.album-card { cursor: pointer; border-radius: 8px; overflow: hidden; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,.08); transition: transform .2s; }
.album-card:hover { transform: translateY(-2px); }
.cover-wrapper { aspect-ratio: 1; overflow: hidden; background: #f5f5f5; }
.cover-wrapper img { width: 100%; height: 100%; object-fit: cover; }
.placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #ccc; }
.info { padding: 10px 12px; }
.title { font-size: 14px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.count { font-size: 12px; color: #999; margin-top: 4px; }
.loading-row { text-align: center; padding: 24px; }
</style>
