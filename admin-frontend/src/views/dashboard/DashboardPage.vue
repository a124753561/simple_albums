<template>
  <div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const stats = ref({ albums: 0, photos: 0, users: 0 })

onMounted(async () => {
  try {
    const res = await request.get('/dashboard/stats/')
    stats.value = res.data.data
  } catch {}
})
</script>

<style scoped>
.stat-card { cursor: pointer; }
.stat-card h2 { margin: 0; font-size: 32px; color: #409eff; }
</style>
