<template>
  <div>
    <el-button type="primary" @click="openDialog()">新增分类</el-button>
    <el-table :data="categories" row-key="id" style="margin-top:16px" v-loading="loading"
              :tree-props="{ children: 'children', hasChildren: 'hasChildren' }" border>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button text type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button v-if="!row.parent" text type="success" @click="openDialog(null, row)">添加子分类</el-button>
          <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
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
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

interface Category {
  id: number; name: string; parent: number | null; sort_order: number; children: Category[]
}

const categories = ref<Category[]>([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const parentId = ref<number | null>(null)
const form = ref({ name: '', sort_order: 0 })

const dialogTitle = computed(() => {
  if (parentId.value) return '添加子分类'
  return isEdit.value ? '编辑分类' : '新增分类'
})

async function fetchCategories() {
  loading.value = true
  const res = await request.get('/categories/')
  categories.value = res.data.data || []
  loading.value = false
}

function openDialog(row?: Category, parent?: Category) {
  if (row) {
    isEdit.value = true
    editId.value = row.id
    parentId.value = null
    form.value = { name: row.name, sort_order: row.sort_order }
  } else if (parent) {
    isEdit.value = false
    editId.value = null
    parentId.value = parent.id
    form.value = { name: '', sort_order: 0 }
  } else {
    isEdit.value = false
    editId.value = null
    parentId.value = null
    form.value = { name: '', sort_order: 0 }
  }
  dialogVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    const data: any = { name: form.value.name, sort_order: form.value.sort_order }
    if (parentId.value) data.parent = parentId.value
    if (isEdit.value) {
      await request.patch(`/categories/${editId.value}/`, data)
    } else {
      await request.post('/categories/', data)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    fetchCategories()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: Category) {
  await ElMessageBox.confirm('确定删除该分类？', '确认', { type: 'warning' })
  try {
    await request.delete(`/categories/${row.id}/`)
    ElMessage.success('删除成功')
    fetchCategories()
  } catch {
    // error message handled by interceptor
  }
}

onMounted(fetchCategories)
</script>
