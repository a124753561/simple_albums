<template>
  <div class="contact-page">
    <h2 class="page-title">联系档案</h2>
    <van-cell-group inset>
      <van-cell title="微信号" :value="contact.wechat || '未设置'" />
      <van-cell title="邮箱" :value="contact.email || '未设置'" />
      <van-cell title="电话" :value="contact.phone || '未设置'" />
    </van-cell-group>
    <div v-if="contact.wechat_qrcode" class="qrcode-section">
      <h3>微信二维码</h3>
      <van-image :src="contact.wechat_qrcode" fit="contain" class="qrcode-img" />
    </div>
    <div v-if="contact.about" class="about">
      <h3>关于</h3>
      <p>{{ contact.about }}</p>
    </div>
    <van-empty v-if="!loading && !hasData" description="暂无联系信息" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'

const contact = ref<any>({})
const loading = ref(true)

const hasData = computed(() => {
  return contact.value.wechat || contact.value.wechat_qrcode || contact.value.email || contact.value.phone || contact.value.about
})

onMounted(async () => {
  try {
    const res = await request.get('/public/contact/')
    contact.value = res.data.data || {}
  } catch {}
  loading.value = false
})
</script>

<style scoped>
.page-title { margin-bottom: 20px; font-size: 22px; }
.qrcode-section { margin-top: 24px; padding: 0 16px; text-align: center; }
.qrcode-section h3 { margin-bottom: 12px; }
.qrcode-img { width: 200px; height: 200px; margin: 0 auto; }
.about { margin-top: 24px; padding: 0 16px; }
.about h3 { margin-bottom: 8px; }
.about p { color: #666; line-height: 1.6; }
</style>
