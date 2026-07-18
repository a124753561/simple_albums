<template>
  <el-card>
    <template #header>联系档案</template>
    <el-form :model="form" label-width="80px" style="max-width:500px">
      <el-form-item label="微信号"><el-input v-model="form.wechat" /></el-form-item>
      <el-form-item label="微信二维码">
        <div style="display:flex;align-items:flex-start;gap:12px">
          <el-upload
            :action="uploadUrl"
            :show-file-list="false"
            :before-upload="beforeUpload"
            :http-request="handleUpload"
            accept="image/*"
          >
            <img v-if="form.wechat_qrcode" :src="form.wechat_qrcode" class="qrcode-preview" />
            <el-button v-else type="primary" :loading="uploading">
              <el-icon><Upload /></el-icon> 上传二维码
            </el-button>
          </el-upload>
          <el-button
            v-if="form.wechat_qrcode"
            type="danger" text
            @click="form.wechat_qrcode = ''"
          >删除</el-button>
        </div>
      </el-form-item>
      <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
      <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
      <el-form-item label="简介"><el-input v-model="form.about" type="textarea" /></el-form-item>
      <el-form-item>
        <el-button type="primary" @click="save" :loading="saving">保存设置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import request from '@/utils/request'

const form = ref({ wechat: '', wechat_qrcode: '', email: '', phone: '', about: '' })
const saving = ref(false)
const uploading = ref(false)

const uploadUrl = import.meta.env.VITE_API_BASE_URL + '/configs/upload/'

onMounted(async () => {
  const res = await request.get('/configs/')
  form.value = { ...form.value, ...res.data.data }
})

function beforeUpload(file: File) {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  return true
}

async function handleUpload(options: any) {
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', options.file)
    const res = await request.post('/configs/upload/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    form.value.wechat_qrcode = res.data.data.url
    ElMessage.success('上传成功')
  } catch {
    // handled by interceptor
  } finally {
    uploading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    await request.put('/configs/update/', form.value)
    ElMessage.success('保存成功')
  } finally { saving.value = false }
}
</script>

<style scoped>
.qrcode-preview {
  width: 120px; height: 120px; object-fit: contain;
  border: 1px solid #dcdfe6; border-radius: 4px; cursor: pointer;
}
</style>
