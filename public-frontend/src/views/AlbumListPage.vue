<template>
  <div>
    <h2 class="page-title">全部相册</h2>
    <div class="filter-bar">
      <van-dropdown-menu>
        <van-dropdown-item :model-value="selectedCategory" :options="categoryOptions" @change="onCategoryChange" />
      </van-dropdown-menu>
    </div>
    <AlbumCoverGrid :albums="albums" :loading="loading" />
    <div class="load-more" v-if="hasMore">
      <van-button :loading="loadingMore" @click="loadMore" type="primary" plain>加载更多</van-button>
    </div>
    <van-empty v-if="!loading && albums.length === 0" description="暂无相册" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import AlbumCoverGrid from '@/components/AlbumCoverGrid.vue'

const route = useRoute()
const router = useRouter()
const albums = ref<any[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const page = ref(1)
const hasMore = ref(false)
const selectedCategory = ref<number>(Number(route.query.category) || 0)
const categoryOptions = ref([{ text: '全部分类', value: 0 }])

async function fetchCategories() {
  const res = await request.get('/public/categories/')
  const cats = res.data.data || []
  for (const c of cats) {
    categoryOptions.value.push({ text: c.name, value: c.id })
    for (const child of (c.children || [])) {
      categoryOptions.value.push({ text: `  ${child.name}`, value: child.id })
    }
  }
}

async function fetchAlbums(p = 1) {
  const params: any = { page: p }
  if (selectedCategory.value && selectedCategory.value > 0) params.category = selectedCategory.value
  const res = await request.get('/public/albums/', { params })
  const data = res.data.data
  if (p === 1) {
    albums.value = data.results || []
  } else {
    albums.value.push(...(data.results || []))
  }
  hasMore.value = data.results?.length === 20
}

async function onCategoryChange(value: number) {
  selectedCategory.value = value
  router.replace({ query: value && value > 0 ? { category: value } : {} })
  page.value = 1
  loading.value = true
  await fetchAlbums()
  loading.value = false
}

async function loadMore() {
  loadingMore.value = true
  page.value++
  await fetchAlbums(page.value)
  loadingMore.value = false
}

onMounted(async () => {
  await fetchCategories()
  await fetchAlbums()
  loading.value = false
})

watch(() => route.query.category, async (val) => {
  selectedCategory.value = Number(val) || 0
  page.value = 1
  loading.value = true
  await fetchAlbums()
  loading.value = false
})
</script>

<style scoped>
.page-title { margin-bottom: 16px; font-size: 22px; }
.filter-bar { margin-bottom: 16px; }
.load-more { text-align: center; margin-top: 24px; }
</style>
