<template>
  <div>
    <div style="display:flex;gap:12px;margin-bottom:16px">
      <el-input v-model="search" placeholder="搜索相册..." style="width:240px" clearable @change="onSearch"/>
      <el-button type="primary" @click="openDialog()">新增相册</el-button>
      <el-button :type="reorderMode ? 'warning' : 'default'" @click="toggleReorder">{{ reorderMode ? '完成排序' : '重排序' }}</el-button>
    </div>
    <el-table ref="tableRef" :data="albums" row-key="id" v-loading="loading">
      <el-table-column v-if="reorderMode" label="" width="44" fixed="left">
        <template #default>
          <el-icon class="drag-handle" :size="18" style="cursor:grab;color:#999"><Rank /></el-icon>
        </template>
      </el-table-column>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="封面" width="80">
        <template #default="{ row }">
          <el-image v-if="row.cover" :src="row.cover" style="width:50px;height:50px" fit="cover" />
          <span v-else style="color:#ccc">无</span>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="category_name" label="分类" width="120" />
      <el-table-column prop="photo_count" label="图片数" width="80" />
      <el-table-column label="首页显示" width="100">
        <template #default="{ row }">
          <el-switch :model-value="row.homepage_show" @change="toggleHomepage(row)" />
        </template>
      </el-table-column>
      <el-table-column label="禁用" width="80">
        <template #default="{ row }">
          <el-switch :model-value="row.is_disabled" @change="toggleDisabled(row)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button text type="success" @click="$router.push(`/albums/${row.id}/photos`)">图片</el-button>
          <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="onPageSizeChange"
      @current-change="onPageChange"
      style="margin-top:16px;justify-content:flex-end"
    />

    <el-dialog :title="isEdit ? '编辑相册' : '新增相册'" v-model="dialogVisible" width="560px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="请选择" style="width:100%">
            <el-option v-for="c in flatCategories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="封面">
          <div style="display:flex;flex-direction:column;gap:8px">
            <el-image v-if="form.cover" :src="form.cover" fit="cover" style="width:100px;height:100px;border-radius:4px;border:1px solid #ebeef5" />
            <span v-else style="color:#ccc;font-size:13px">暂无封面</span>
            <el-input v-model="form.cover" placeholder="或手动输入URL" size="small" />
          </div>
        </el-form-item>
        <el-form-item label="首页显示"><el-switch v-model="form.homepage_show" /></el-form-item>
        <el-form-item label="禁用"><el-switch v-model="form.is_disabled" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Rank } from '@element-plus/icons-vue'
import { useDraggable } from 'vue-draggable-plus'
import request from '@/utils/request'

const albums = ref<any[]>([])
const flatCategories = ref<any[]>([])
const total = ref(0)
const search = ref('')
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const form = ref({ title: '', description: '', category: '', cover: '', homepage_show: false, is_disabled: false })
const tableRef = ref()
const tbodyRef = ref<HTMLElement | null>(null)
const reorderMode = ref(false)
let sortableDestroy: (() => void) | null = null

async function fetchAlbums() {
  loading.value = true
  const params: any = { page: currentPage.value, page_size: pageSize.value }
  if (search.value) params.search = search.value
  const res = await request.get('/albums/', { params })
  albums.value = res.data.data.results || []
  total.value = res.data.data.count
  loading.value = false
  if (reorderMode.value) initSortable()
}

function initSortable() {
  destroySortable()
  nextTick(() => {
    tbodyRef.value = tableRef.value?.$el?.querySelector('.el-table__body-wrapper tbody') as HTMLElement
    if (tbodyRef.value && albums.value.length > 0) {
      const instance = useDraggable(tbodyRef, albums, {
        handle: '.drag-handle',
        animation: 150,
      })
      sortableDestroy = () => instance.destroy()
    }
  })
}

function destroySortable() {
  if (sortableDestroy) { sortableDestroy(); sortableDestroy = null }
}

function toggleReorder() {
  reorderMode.value = !reorderMode.value
  if (reorderMode.value) {
    initSortable()
  } else {
    destroySortable()
    saveOrder()
  }
}

function saveOrder() {
  const orders = albums.value.map((a: any, idx: number) => ({ id: a.id, sort_order: idx }))
  request.post('/albums/reorder/', { orders }).then(() => {
    ElMessage.success('排序已保存')
  })
}

function onPageChange(page: number) {
  currentPage.value = page
  fetchAlbums()
}

function onPageSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  fetchAlbums()
}

function onSearch() {
  currentPage.value = 1
  fetchAlbums()
}

async function fetchFlatCategories() {
  const res = await request.get('/categories/', { params: { flat: 'true' } })
  flatCategories.value = res.data.data || []
}

function openDialog(row?: any) {
  if (row) {
    isEdit.value = true; editId.value = row.id
    form.value = {
      title: row.title, description: row.description || '', category: row.category,
      cover: row.cover, homepage_show: row.homepage_show, is_disabled: row.is_disabled,
    }
  } else {
    isEdit.value = false; editId.value = null
    form.value = { title: '', description: '', category: '', cover: '', homepage_show: false, is_disabled: false }
  }
  dialogVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (isEdit.value) {
      await request.patch(`/albums/${editId.value}/`, form.value)
    } else {
      await request.post('/albums/', { ...form.value, sort_order: albums.value.length })
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    fetchAlbums()
  } finally { saving.value = false }
}

async function toggleHomepage(row: any) {
  await request.patch(`/albums/${row.id}/`, { homepage_show: !row.homepage_show })
  fetchAlbums()
}

async function toggleDisabled(row: any) {
  await request.patch(`/albums/${row.id}/`, { is_disabled: !row.is_disabled })
  fetchAlbums()
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm('确定删除该相册？将同时删除所有图片！', '确认', { type: 'warning' })
  await request.delete(`/albums/${row.id}/`)
  ElMessage.success('删除成功')
  fetchAlbums()
}

onMounted(() => { fetchAlbums(); fetchFlatCategories() })
</script>

<style scoped>
:deep(.drag-handle) { cursor: grab; }
:deep(.sortable-ghost) { opacity: 0.4; background: #ecf5ff; }
</style>
