<template>
  <div>
    <div class="album-header">
      <h2>{{ album.title }}</h2>
      <p v-if="album.description" class="desc">{{ album.description }}</p>
      <p class="meta">{{ album.photo_count }} 张图片</p>
    </div>
    <div class="photo-grid">
      <div v-for="photo in photos" :key="photo.id" class="photo-item" @click="openViewer(photo)">
        <img :src="photo.url" :alt="photo.name" loading="lazy" />
        <p class="photo-name">{{ photo.name }}</p>
      </div>
    </div>
    <van-empty v-if="!loading && photos.length === 0" description="暂无图片" />

    <!-- Custom Image Viewer -->
    <Teleport to="body">
      <div v-if="viewerVisible" class="viewer-mask" @click.self="closeViewer"
           @touchstart="onTouchStart" @touchend="onTouchEnd">
        <div class="viewer-close" @click="closeViewer">&times;</div>
        <div class="viewer-arrow viewer-prev" @click.stop="prevPhoto">&lsaquo;</div>
        <div class="viewer-arrow viewer-next" @click.stop="nextPhoto">&rsaquo;</div>
        <div class="viewer-body">
          <img :src="currentPhoto?.url" :alt="currentPhoto?.name" class="viewer-img" />
          <p class="viewer-name">{{ currentPhoto?.name }}</p>
          <p class="viewer-counter">{{ viewerIndex + 1 }} / {{ photos.length }}</p>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'

const route = useRoute()
const album = ref<any>({})
const photos = ref<any[]>([])
const loading = ref(true)
const viewerVisible = ref(false)
const viewerIndex = ref(0)
let touchStartX = 0

const currentPhoto = computed(() => photos.value[viewerIndex.value] || null)

onMounted(async () => {
  const res = await request.get(`/public/albums/${route.params.id}/`)
  album.value = res.data.data
  photos.value = res.data.data.photos || []
  loading.value = false
})

function openViewer(photo: any) {
  viewerIndex.value = photos.value.findIndex((p: any) => p.id === photo.id)
  viewerVisible.value = true
}

function closeViewer() { viewerVisible.value = false }

function prevPhoto() {
  if (viewerIndex.value > 0) viewerIndex.value--
}

function nextPhoto() {
  if (viewerIndex.value < photos.value.length - 1) viewerIndex.value++
}

function onTouchStart(e: TouchEvent) { touchStartX = e.touches[0].clientX }
function onTouchEnd(e: TouchEvent) {
  const diff = touchStartX - e.changedTouches[0].clientX
  if (Math.abs(diff) > 50) {
    diff > 0 ? nextPhoto() : prevPhoto()
  }
}

function onKeydown(e: KeyboardEvent) {
  if (!viewerVisible.value) return
  if (e.key === 'ArrowLeft') prevPhoto()
  else if (e.key === 'ArrowRight') nextPhoto()
  else if (e.key === 'Escape') closeViewer()
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => document.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.album-header { margin-bottom: 20px; }
.album-header h2 { font-size: 22px; margin-bottom: 8px; }
.desc { color: #666; font-size: 14px; margin-bottom: 4px; }
.meta { color: #999; font-size: 13px; }
.photo-grid {
  display: grid; gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}
@media (max-width: 768px) {
  .photo-grid { grid-template-columns: repeat(3, 1fr); gap: 8px; }
}
.photo-item {
  cursor: pointer; border-radius: 8px; overflow: hidden;
  background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,.08);
  display: flex; flex-direction: column;
  transition: box-shadow .2s;
}
.photo-item:hover { box-shadow: 0 4px 16px rgba(0,0,0,.12); }
.photo-item img {
  width: 100%; aspect-ratio: 1; object-fit: cover;
  display: block;
}
.photo-name {
  text-align: center; font-size: 13px; color: #333;
  padding: 8px 8px 10px; line-height: 1.4;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* Viewer */
.viewer-mask {
  position: fixed; inset: 0; z-index: 3000;
  background: rgba(0,0,0,.92); display: flex;
  align-items: center; justify-content: center;
}
.viewer-close {
  position: absolute; top: 16px; right: 20px; z-index: 10;
  font-size: 36px; color: #fff; cursor: pointer; line-height: 1;
  opacity: .7; transition: opacity .2s;
}
.viewer-close:hover { opacity: 1; }
.viewer-arrow {
  position: absolute; top: 50%; transform: translateY(-50%); z-index: 10;
  font-size: 48px; color: #fff; cursor: pointer; opacity: .6;
  width: 56px; height: 56px; display: flex; align-items: center; justify-content: center;
  transition: opacity .2s; user-select: none;
}
.viewer-arrow:hover { opacity: 1; }
.viewer-prev { left: 8px; }
.viewer-next { right: 8px; }
.viewer-body {
  display: flex; flex-direction: column; align-items: center;
  max-width: 90vw; max-height: 90vh;
}
.viewer-img {
  max-width: 90vw; max-height: 72vh; object-fit: contain;
  border-radius: 4px;
}
.viewer-name {
  color: #fff; font-size: 16px; margin-top: 16px; text-align: center;
  max-width: 80vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.viewer-counter {
  color: #999; font-size: 13px; margin-top: 6px;
}
@media (max-width: 768px) {
  .viewer-arrow { font-size: 36px; width: 40px; height: 40px; }
  .viewer-prev { left: 2px; }
  .viewer-next { right: 2px; }
  .viewer-img { max-width: 96vw; }
}
</style>
