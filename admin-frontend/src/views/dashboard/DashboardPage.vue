<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card" @click="$router.push('/albums')">
          <template #header><span>相册总数</span></template>
          <h2>{{ stats.albums }}</h2>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card" @click="$router.push('/albums')">
          <template #header><span>图片总数</span></template>
          <h2>{{ stats.photos }}</h2>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card" @click="$router.push('/users')">
          <template #header><span>用户数</span></template>
          <h2>{{ stats.users }}</h2>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card" v-if="stats.uv_data && stats.uv_data.points && stats.uv_data.points.length > 0">
      <template #header>
        <span>UV 趋势</span>
        <span class="card-tip">（近7天独立访客）</span>
      </template>
      <v-chart :option="uvChartOption" style="height:300px" autoresize />
    </el-card>

    <el-row :gutter="20" style="margin-bottom:20px">
      <el-col :span="12">
        <el-card class="top-card" v-if="stats.top_albums && stats.top_albums.length > 0">
          <template #header>
            <span>热门相册 Top {{ stats.top_albums.length }}</span>
            <span class="card-tip">（近7天访问量汇总）</span>
          </template>
          <div class="top-list">
            <div v-for="(album, idx) in stats.top_albums" :key="album.id" class="top-item"
                 @click="goToAlbum(album.id)">
              <span class="top-rank" :class="'rank-' + (Number(idx) + 1)">{{ Number(idx) + 1 }}</span>
              <el-image :src="album.cover" fit="cover" class="top-thumb" />
              <div class="top-info">
                <p class="top-name">{{ album.title }}</p>
              </div>
              <span class="top-count">{{ formatCount(album.total_views) }} 次</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="top-card" v-if="stats.top_photos && stats.top_photos.length > 0">
          <template #header>
            <span>热门图片 Top {{ stats.top_photos.length }}</span>
            <span class="card-tip">（近7天访问量）</span>
          </template>
          <div class="top-list">
            <div v-for="(photo, idx) in stats.top_photos" :key="photo.id" class="top-item"
                 @click="goToAlbum(photo.album_id)">
              <span class="top-rank" :class="'rank-' + (Number(idx) + 1)">{{ Number(idx) + 1 }}</span>
              <el-image :src="photo.url" fit="cover" class="top-thumb" />
              <div class="top-info">
                <p class="top-name">{{ photo.name }}</p>
                <p class="top-album">{{ photo.album_title }}</p>
              </div>
              <span class="top-count">{{ formatCount(photo.view_count) }} 次</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="(!stats.top_photos || stats.top_photos.length === 0) && (!stats.top_albums || stats.top_albums.length === 0)" description="暂无访问数据" :image-size="80" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([LineChart, GridComponent, TooltipComponent, CanvasRenderer])

const router = useRouter()
const stats = ref<Record<string, any>>({})

const uvChartOption = computed(() => {
  const uv = stats.value.uv_data
  if (!uv) return {}
  return {
    tooltip: {
      trigger: 'axis',
      formatter: (p: any) => `${p[0].axisValue}<br/>UV: <b>${p[0].value}</b>`,
    },
    grid: { top: 10, right: 20, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: uv.points.map((s: string) => s.slice(5)),
      axisLine: { lineStyle: { color: '#ddd' } },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: '#f0f0f0' } },
    },
    series: [{
      data: uv.values,
      type: 'line',
      smooth: true,
      areaStyle: { color: 'rgba(64,158,255,0.15)' },
      lineStyle: { color: '#409eff', width: 2 },
      itemStyle: { color: '#409eff' },
    }],
  }
})

onMounted(async () => {
  try {
    const res = await request.get('/dashboard/stats/')
    stats.value = res.data.data
  } catch {}
})

function goToAlbum(albumId: number) {
  router.push(`/albums/${albumId}/photos`)
}

function formatCount(n: number): string {
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  return n.toLocaleString()
}
</script>

<style scoped>
.dashboard { max-width: 1000px; }
.stat-card { cursor: pointer; }
.stat-card h2 { margin: 0; font-size: 32px; color: #409eff; }
.chart-card { margin: 20px 0; }
.top-card { margin-top: 0; }
.card-tip { font-size: 12px; color: #999; font-weight: normal; }
.top-list { display: flex; flex-direction: column; gap: 8px; }
.top-item {
  display: flex; align-items: center; gap: 12px; padding: 8px;
  border-radius: 6px; cursor: pointer; transition: background .2s;
}
.top-item:hover { background: #f5f7fa; }
.top-rank {
  flex-shrink: 0; width: 24px; height: 24px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: bold; color: #fff; background: #c0c4cc;
}
.top-rank.rank-1 { background: #f56c6c; }
.top-rank.rank-2 { background: #e6a23c; }
.top-rank.rank-3 { background: #409eff; }
.top-thumb {
  flex-shrink: 0; width: 48px; height: 48px; border-radius: 4px;
}
.top-info { flex: 1; min-width: 0; }
.top-name {
  font-size: 14px; color: #333; margin: 0;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.top-album {
  font-size: 12px; color: #999; margin: 2px 0 0;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.top-count {
  flex-shrink: 0; font-size: 13px; color: #409eff; font-weight: 500;
}
</style>
