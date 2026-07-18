<template>
  <div>
    <h2 class="page-title">精选相册</h2>
    <AlbumCoverGrid :albums="albums" :loading="loading" />
    <div class="load-more" v-if="hasMore">
      <van-button :loading="loadingMore" @click="loadMore" type="primary" plain>加载更多</van-button>
    </div>
    <van-empty v-if="!loading && albums.length === 0" description="暂无相册" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import AlbumCoverGrid from '@/components/AlbumCoverGrid.vue'

const albums = ref<any[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const page = ref(1)
const hasMore = ref(false)

async function fetchAlbums(p = 1) {
  const res = await request.get('/public/homepage-albums/', { params: { page: p } })
  const data = res.data.data
  if (p === 1) {
    albums.value = data.results || []
  } else {
    albums.value.push(...(data.results || []))
  }
  hasMore.value = data.results?.length === 20
}

onMounted(async () => {
  await fetchAlbums()
  loading.value = false
})

async function loadMore() {
  loadingMore.value = true
  page.value++
  await fetchAlbums(page.value)
  loadingMore.value = false
}
</script>

<style scoped>
.page-title { margin-bottom: 16px; font-size: 22px; }
.load-more { text-align: center; margin-top: 24px; }
</style>
