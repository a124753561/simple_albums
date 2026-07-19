<template>
  <div>
    <el-card style="margin-bottom:16px">
      <el-form :model="album" label-width="80px" inline>
        <el-form-item label="标题"><el-input v-model="album.title" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="album.category" style="width:200px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="首页显示"><el-switch v-model="album.homepage_show" /></el-form-item>
        <el-form-item><el-button type="primary" @click="saveAlbum">保存相册</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
          <span>图片管理 ({{ photos.length }} 张)</span>
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            <template v-if="!batchMode">
              <el-button type="primary" @click="uploadVisible = true">选择文件上传</el-button>
              <el-button @click="toggleBatchMode">操作</el-button>
              <el-button-group>
                <el-button :type="viewMode === 'grid' ? 'primary' : 'default'" @click="viewMode = 'grid'">
                  <el-icon><Grid /></el-icon>
                </el-button>
                <el-button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'">
                  <el-icon><List /></el-icon>
                </el-button>
              </el-button-group>
            </template>
            <template v-else>
              <el-checkbox
                :model-value="allSelected"
                :indeterminate="isIndeterminate"
                @change="(val: boolean) => val ? selectAll() : deselectAll()"
              >全选</el-checkbox>
              <el-button type="danger" :disabled="selectedIds.length === 0" @click="batchDelete">
                批量删除 ({{ selectedIds.length }})
              </el-button>
              <el-button type="success" :disabled="selectedIds.length !== 1" @click="setAsCover">
                设为首页
              </el-button>
              <el-button text @click="deselectAll" :disabled="selectedIds.length === 0">取消全选</el-button>
              <el-button type="warning" @click="toggleBatchMode">退出操作</el-button>
            </template>
          </div>
        </div>
      </template>

      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" ref="gridRef" class="photo-grid" @mousedown="onGridMouseDown">
        <div v-for="photo in photos" :key="photo.id" class="photo-item"
             :data-photo-id="photo.id"
             :class="{ 'is-selected': selectedIds.includes(photo.id), 'is-batch-mode': batchMode }">
          <div class="photo-image-wrap">
            <el-image :src="photo.url" fit="cover"
                      :preview-src-list="batchMode ? undefined : previewList"
                      :initial-index="photos.findIndex(p => p.id === photo.id)"
                      :hide-on-click-modal="true" />
            <el-checkbox v-if="batchMode" :model-value="selectedIds.includes(photo.id)"
                         @change="(val: boolean) => toggleSelect(photo.id, val)"
                         class="photo-checkbox" />
          </div>
          <div class="photo-name-wrap" @click.stop>
            <input v-if="editingId === photo.id" v-model="editName" v-focus
                   class="photo-name-input" @blur="saveName(photo)" @keydown.enter="($event.target as HTMLElement).blur()" />
            <span v-else class="photo-name" @click="startEdit(photo)" :title="photo.name">
              {{ photo.name || '未命名' }}
            </span>
          </div>
        </div>
        <div v-if="photos.length === 0" style="color:#999;padding:40px;text-align:center;width:100%">
          暂无图片，请上传
        </div>
        <div v-if="batchMode && dragSelect.active" class="drag-overlay" :style="dragOverlayStyle" />
      </div>

      <!-- List View -->
      <div v-if="viewMode === 'list'" ref="listRef" class="photo-list">
        <div v-for="photo in photos" :key="photo.id" class="photo-list-item"
             :data-photo-id="photo.id"
             :class="{ 'is-selected': selectedIds.includes(photo.id), 'is-batch-mode': batchMode }">
          <el-checkbox v-if="batchMode" :model-value="selectedIds.includes(photo.id)"
                       @change="(val: boolean) => toggleSelect(photo.id, val)" />
          <el-image :src="photo.url" fit="cover"
                    style="width:80px;height:80px;flex-shrink:0;border-radius:4px"
                    :preview-src-list="batchMode ? undefined : previewList"
                    :initial-index="photos.findIndex(p => p.id === photo.id)"
                    :hide-on-click-modal="true" />
          <div class="photo-list-info">
            <div class="photo-list-name" @click.stop>
              <input v-if="editingId === photo.id" v-model="editName" v-focus
                     class="photo-name-input" @blur="saveName(photo)" @keydown.enter="($event.target as HTMLElement).blur()" />
              <span v-else class="photo-name" @click="startEdit(photo)" :title="photo.name">
                {{ photo.name || '未命名' }}
              </span>
            </div>
            <div class="photo-list-meta">
              <span>{{ formatSize(photo.file_size) }}</span>
              <span>{{ photo.width }} x {{ photo.height }}</span>
            </div>
          </div>
        </div>
        <div v-if="photos.length === 0" style="color:#999;padding:40px;text-align:center;width:100%">
          暂无图片，请上传
        </div>
      </div>
    </el-card>

    <!-- Upload Dialog -->
    <el-dialog title="上传图片" v-model="uploadVisible" width="580px" :close-on-click-modal="false">
      <div class="upload-area" :class="{ 'is-dragover': isDragOver }"
           @dragover.prevent="onDragOver" @dragleave="onDragLeave" @drop.prevent="onDrop"
           @click="triggerFileInput">
        <input ref="fileInputRef" type="file" multiple
               accept="image/jpeg,image/png,image/gif,image/webp"
               style="display:none" @change="onFileChange" />
        <el-icon :size="48" color="#c0c4cc"><UploadFilled /></el-icon>
        <p style="margin-top:12px;color:#909399">点击选择文件，或将文件拖拽到此区域</p>
        <p style="color:#c0c4cc;font-size:12px">支持 JPG / PNG / GIF / WebP，单次最多 200 张</p>
      </div>

      <div v-if="pendingFiles.length > 0" class="pending-list">
        <div v-for="(f, idx) in pendingFiles" :key="idx" class="pending-item">
          <img :src="f.preview" class="pending-thumb" />
          <span class="pending-name">{{ f.file.name }}</span>
          <el-icon class="pending-del" @click="removePending(idx)"><Delete /></el-icon>
        </div>
      </div>

      <template #footer>
        <el-button @click="cancelUpload">取消</el-button>
          <el-button type="primary" :loading="uploading" :disabled="pendingFiles.length === 0" @click="doUpload">
            {{ uploading ? `上传中 (${uploadProgress.current}/${uploadProgress.total})` : `上传 ${pendingFiles.length} 张` }}
          </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Delete, Grid, List } from '@element-plus/icons-vue'
import { useDraggable } from 'vue-draggable-plus'
import request from '@/utils/request'

const route = useRoute()
const albumId = Number(route.params.id)
const album = ref<any>({ title: '', category: '', homepage_show: false })
const categories = ref<any[]>([])
const photos = ref<any[]>([])
const selectedIds = ref<number[]>([])
const batchMode = ref(false)
const viewMode = ref<'grid' | 'list'>('grid')
const gridRef = ref<HTMLElement | null>(null)
const listRef = ref<HTMLElement | null>(null)

const previewList = computed(() => photos.value.map(p => p.url))
const allSelected = computed(() => photos.value.length > 0 && selectedIds.value.length === photos.value.length)
const isIndeterminate = computed(() => selectedIds.value.length > 0 && selectedIds.value.length < photos.value.length)

let sortableDestroy: (() => void) | null = null

function enableSortable() {
  if (sortableDestroy) { sortableDestroy(); sortableDestroy = null }
  const elRef = viewMode.value === 'grid' ? gridRef : listRef
  const instance = useDraggable(elRef, photos, {
    animation: 150,
    draggable: viewMode.value === 'grid' ? '.photo-item' : '.photo-list-item',
    onEnd: onPhotoDragEnd,
    disabled: batchMode.value,
  })
  sortableDestroy = () => instance.destroy()
}

function disableSortable() {
  if (sortableDestroy) { sortableDestroy(); sortableDestroy = null }
}

function onPhotoDragEnd() {
  const orders = photos.value.map((p: any, idx: number) => ({ id: p.id, sort_order: idx }))
  request.post(`/albums/${albumId}/photos/reorder/`, { orders })
}

watch(batchMode, (val) => {
  if (val) {
    disableSortable()
  } else {
    nextTick(() => enableSortable())
  }
})

watch(viewMode, () => {
  if (!batchMode.value) {
    nextTick(() => enableSortable())
  }
})

function selectAll() { selectedIds.value = photos.value.map((p: any) => p.id) }
function deselectAll() { selectedIds.value = [] }

async function setAsCover() {
  if (selectedIds.value.length !== 1) return
  const photoId = selectedIds.value[0]
  await request.post(`/albums/${albumId}/photos/${photoId}/set-cover/`)
  ElMessage.success('已设为首页封面')
  const targetPhoto = photos.value.find((p: any) => p.id === photoId)
  if (targetPhoto) album.value.cover = targetPhoto.url
  fetchAlbum()
}

function formatSize(bytes: number): string {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// Inline rename
const editingId = ref<number | null>(null)
const editName = ref('')

const vFocus = { mounted: (el: HTMLInputElement) => el.focus() }

function startEdit(photo: any) {
  editingId.value = photo.id
  editName.value = photo.name || ''
}

async function saveName(photo: any) {
  const newName = editName.value.trim()
  editingId.value = null
  if (newName && newName !== photo.name) {
    await request.patch(`/albums/${albumId}/photos/${photo.id}/`, { name: newName })
    photo.name = newName
    ElMessage.success('已改名')
  }
}

// Upload dialog
const uploadVisible = ref(false)
const uploading = ref(false)
const uploadProgress = ref({ current: 0, total: 0 })
const isDragOver = ref(false)
const pendingFiles = ref<{ file: File; preview: string }[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)

function triggerFileInput() { fileInputRef.value?.click() }
function onDragOver() { isDragOver.value = true }
function onDragLeave() { isDragOver.value = false }

function addFiles(files: FileList | File[]) {
  const accepted = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  for (const f of Array.from(files)) {
    if (!accepted.includes(f.type)) continue
    if (pendingFiles.value.length >= 200) break
    pendingFiles.value.push({ file: f, preview: URL.createObjectURL(f) })
  }
}

function onDrop(e: DragEvent) {
  isDragOver.value = false
  if (e.dataTransfer?.files) addFiles(e.dataTransfer.files)
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) addFiles(input.files)
  input.value = ''
}

function removePending(idx: number) {
  URL.revokeObjectURL(pendingFiles.value[idx].preview)
  pendingFiles.value.splice(idx, 1)
}

function cancelUpload() {
  pendingFiles.value.forEach(f => URL.revokeObjectURL(f.preview))
  pendingFiles.value = []
  uploadVisible.value = false
}

const BATCH_SIZE = 5

async function doUpload() {
  uploading.value = true
  const total = pendingFiles.value.length
  const totalBatches = Math.ceil(total / BATCH_SIZE)
  uploadProgress.value = { current: 0, total: totalBatches }
  let successCount = 0
  for (let i = 0; i < total; i += BATCH_SIZE) {
    const batch = pendingFiles.value.slice(i, i + BATCH_SIZE)
    const formData = new FormData()
    for (const f of batch) formData.append('files', f.file)
    try {
      await request.post(`/albums/${albumId}/photos/upload/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,
      })
      successCount++
    } catch { /* 单批失败继续传下一批 */ }
    uploadProgress.value = { current: Math.floor(i / BATCH_SIZE) + 1, total: totalBatches }
  }
  if (successCount > 0) {
    ElMessage.success(`上传完成 (${successCount}/${totalBatches} 批)`)
  }
  pendingFiles.value.forEach(f => URL.revokeObjectURL(f.preview))
  pendingFiles.value = []
  uploadVisible.value = false
  uploading.value = false
  fetchPhotos(); fetchAlbum()
}

// Drag select
const dragSelect = ref({ active: false, startX: 0, startY: 0, endX: 0, endY: 0 })

const dragOverlayStyle = computed(() => {
  const d = dragSelect.value
  return {
    left: `${Math.min(d.startX, d.endX)}px`,
    top: `${Math.min(d.startY, d.endY)}px`,
    width: `${Math.abs(d.endX - d.startX)}px`,
    height: `${Math.abs(d.endY - d.startY)}px`,
  }
})

function currentGridRef() {
  return viewMode.value === 'grid' ? gridRef.value : listRef.value
}

function toggleBatchMode() {
  batchMode.value = !batchMode.value
  if (!batchMode.value) selectedIds.value = []
}

function toggleSelect(id: number, val: boolean) {
  if (val) {
    selectedIds.value = [...selectedIds.value, id]
  } else {
    selectedIds.value = selectedIds.value.filter(i => i !== id)
  }
}

function onGridMouseDown(e: MouseEvent) {
  if (!batchMode.value) return
  if ((e.target as HTMLElement).closest(viewMode.value === 'grid' ? '.photo-item' : '.photo-list-item')) return
  const el = currentGridRef()
  const rect = el?.getBoundingClientRect() ?? null
  if (!rect) return
  dragSelect.value = {
    active: true,
    startX: e.clientX - rect.left, startY: e.clientY - rect.top,
    endX: e.clientX - rect.left, endY: e.clientY - rect.top,
  }
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

function onMouseMove(e: MouseEvent) {
  const el = currentGridRef()
  const rect = el?.getBoundingClientRect() ?? null
  if (!rect) return
  dragSelect.value.endX = Math.max(0, Math.min(e.clientX - rect.left, rect.width))
  dragSelect.value.endY = Math.max(0, Math.min(e.clientY - rect.top, rect.height))
}

function onMouseUp() {
  if (!dragSelect.value.active) return
  const ds = dragSelect.value
  const selRect = {
    left: Math.min(ds.startX, ds.endX),
    top: Math.min(ds.startY, ds.endY),
    right: Math.max(ds.startX, ds.endX),
    bottom: Math.max(ds.startY, ds.endY),
  }
  const el = currentGridRef()
  const rect = el?.getBoundingClientRect() ?? null
  if (rect) {
    const selector = viewMode.value === 'grid' ? '.photo-item' : '.photo-list-item'
    const items = el!.querySelectorAll(selector)
    items.forEach(el => {
      const itemRect = el.getBoundingClientRect()
      const ix = itemRect.left - rect.left + itemRect.width / 2
      const iy = itemRect.top - rect.top + itemRect.height / 2
      if (ix >= selRect.left && ix <= selRect.right && iy >= selRect.top && iy <= selRect.bottom) {
        const id = Number((el as HTMLElement).dataset.photoId)
        if (!selectedIds.value.includes(id)) {
          selectedIds.value = [...selectedIds.value, id]
        }
      }
    })
  }
  dragSelect.value.active = false
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
}

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
  disableSortable()
})

async function fetchAlbum() {
  const res = await request.get(`/albums/${albumId}/`)
  album.value = res.data.data
}
async function fetchCategories() {
  const res = await request.get('/categories/', { params: { flat: 'true' } })
  categories.value = res.data.data || []
}
async function fetchPhotos() {
  const res = await request.get(`/albums/${albumId}/photos/`)
  photos.value = res.data.data || []
  if (!batchMode.value) {
    nextTick(() => enableSortable())
  }
}

async function saveAlbum() {
  await request.patch(`/albums/${albumId}/`, {
    title: album.value.title, category: album.value.category, homepage_show: album.value.homepage_show,
  })
  ElMessage.success('保存成功')
}

async function batchDelete() {
  await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 张图片？`, '确认', { type: 'warning' })
  await request.post(`/albums/${albumId}/photos/batch/`, {
    action: 'delete', photo_ids: selectedIds.value,
  })
  ElMessage.success('删除成功')
  selectedIds.value = []
  fetchPhotos(); fetchAlbum()
}

onMounted(() => { fetchAlbum(); fetchCategories(); fetchPhotos() })
</script>

<style scoped>
/* Grid View */
.photo-grid {
  display: flex; flex-wrap: wrap; gap: 16px;
  position: relative; user-select: none;
}
.photo-item { position: relative; }
.photo-item.is-batch-mode { cursor: pointer; }
.photo-item.is-selected::after {
  content: ''; position: absolute; inset: -2px;
  border: 2px solid #409eff; border-radius: 4px; pointer-events: none;
}
.photo-image-wrap {
  position: relative; width: 180px; height: 180px;
}
.photo-image-wrap .el-image {
  width: 100%; height: 100%;
}
.photo-checkbox {
  position: absolute; bottom: 4px; left: 4px; z-index: 2;
}
.photo-name-wrap {
  text-align: center; margin-top: 6px; max-width: 180px;
}
.photo-name {
  font-size: 13px; color: #333;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  display: inline-block; max-width: 100%;
  cursor: text; padding: 2px 4px;
}
.photo-name:hover { background: #f0f0f0; border-radius: 2px; }

/* List View */
.photo-list {
  display: flex; flex-direction: column; gap: 8px;
  position: relative; user-select: none;
}
.photo-list-item {
  display: flex; align-items: center; gap: 12px;
  padding: 8px; border: 1px solid #ebeef5; border-radius: 6px;
}
.photo-list-item:hover { background: #f5f7fa; }
.photo-list-item.is-batch-mode { cursor: pointer; }
.photo-list-item.is-selected { border-color: #409eff; background: #ecf5ff; }
.photo-list-info { flex: 1; min-width: 0; }
.photo-list-name { font-size: 14px; color: #333; }
.photo-list-meta { font-size: 12px; color: #999; margin-top: 4px; display: flex; gap: 16px; }

.photo-name-input {
  width: 160px; font-size: 13px; text-align: center;
  border: 1px solid #409eff; border-radius: 2px; padding: 2px 4px;
  outline: none;
}
.photo-name-input:focus { border-color: #409eff; }

.drag-overlay {
  position: absolute; z-index: 10;
  background: rgba(64, 158, 255, 0.15);
  border: 1px dashed #409eff; pointer-events: none;
}

/* Upload dialog */
.upload-area {
  border: 2px dashed #dcdfe6; border-radius: 8px;
  padding: 48px 0; text-align: center; cursor: pointer;
  transition: border-color .2s, background .2s;
}
.upload-area:hover, .upload-area.is-dragover {
  border-color: #409eff; background: #ecf5ff;
}
.pending-list {
  max-height: 240px; overflow-y: auto; margin-top: 16px;
}
.pending-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 0; border-bottom: 1px solid #f0f0f0;
}
.pending-thumb {
  width: 48px; height: 48px; object-fit: cover; border-radius: 4px; flex-shrink: 0;
}
.pending-name {
  flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px;
}
.pending-del {
  cursor: pointer; color: #f56c6c; flex-shrink: 0;
}

:deep(.sortable-ghost) { opacity: 0.4; background: #ecf5ff; }
</style>
