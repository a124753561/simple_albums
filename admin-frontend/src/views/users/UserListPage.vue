<template>
  <div>
    <el-button type="primary" @click="openDialog()">新增用户</el-button>
    <el-table :data="users" style="margin-top:16px" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-switch :model-value="row.is_active" @change="toggleActive(row)" />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button text type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="isEdit ? '编辑用户' : '新增用户'" v-model="dialogVisible" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password :placeholder="isEdit ? '留空不修改' : ''" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const users = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const form = ref({ username: '', password: '', is_active: true })

async function fetchUsers() {
  loading.value = true
  const res = await request.get('/users/')
  users.value = res.data.data.results || []
  loading.value = false
}

function openDialog(row?: any) {
  if (row) {
    isEdit.value = true
    editId.value = row.id
    form.value = { username: row.username, password: '', is_active: row.is_active }
  } else {
    isEdit.value = false
    editId.value = null
    form.value = { username: '', password: '', is_active: true }
  }
  dialogVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (isEdit.value) {
      const data: any = { username: form.value.username, is_active: form.value.is_active }
      if (form.value.password) data.password = form.value.password
      await request.patch(`/users/${editId.value}/`, data)
      ElMessage.success('更新成功')
    } else {
      await request.post('/users/', form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchUsers()
  } finally {
    saving.value = false
  }
}

async function toggleActive(row: any) {
  await request.patch(`/users/${row.id}/`, { is_active: !row.is_active })
  fetchUsers()
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm('确定删除该用户？', '确认', { type: 'warning' })
  await request.delete(`/users/${row.id}/`)
  ElMessage.success('删除成功')
  fetchUsers()
}

onMounted(fetchUsers)
</script>
