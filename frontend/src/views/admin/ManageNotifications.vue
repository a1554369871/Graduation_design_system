<template>
  <div class="manage-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>管理通知</span>
        </div>
      </template>

      <div v-if="loading" style="text-align:center;padding:40px">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
      </div>

      <el-empty v-else-if="notifications.length === 0" description="暂无通知" />

      <el-table v-else :data="notifications" stripe>
        <el-table-column label="标题" min-width="200">
          <template #default="{ row }">
            <span>{{ row.title }}</span>
            <el-tag v-if="row.is_expired" type="danger" size="small" style="margin-left:8px">已过期</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="内容" min-width="250" show-overflow-tooltip />
        <el-table-column prop="sender_name" label="发送人" width="100" />
        <el-table-column label="发送时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="过期时间" width="160">
          <template #default="{ row }">
            <span v-if="row.expires_at" :style="{ color: row.is_expired ? '#f56c6c' : '#909399' }">
              {{ formatTime(row.expires_at) }}
            </span>
            <span v-else style="color:#c0c4cc">永不过期</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total > perPage" class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          :page-size="perPage"
          :total="total"
          layout="prev, pager, next"
          @current-change="fetchNotifications"
        />
      </div>
    </el-card>

    <el-dialog v-model="editDialog.visible" title="编辑通知" width="500px">
      <el-form label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="editDialog.form.title" maxlength="256" show-word-limit />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="editDialog.form.content"
            type="textarea"
            :rows="4"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="过期时间">
          <el-date-picker
            v-model="editDialog.form.expires_at"
            type="datetime"
            placeholder="设置过期时间（留空为永不过期）"
            style="width:100%"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import {
  getAllAdminNotifications,
  updateAdminNotification,
  deleteAdminNotification,
} from '../../api/notification'

const notifications = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(20)
const total = ref(0)
const saving = ref(false)

const editDialog = ref({
  visible: false,
  currentId: null,
  form: {
    title: '',
    content: '',
    expires_at: null,
  },
})

function formatTime(timeStr) {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function fetchNotifications() {
  loading.value = true
  try {
    const res = await getAllAdminNotifications({ page: page.value, per_page: perPage.value })
    notifications.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function openEdit(row) {
  editDialog.value = {
    visible: true,
    currentId: row.id,
    form: {
      title: row.title,
      content: row.content || '',
      expires_at: row.expires_at || null,
    },
  }
}

async function handleSave() {
  saving.value = true
  try {
    await updateAdminNotification(editDialog.value.currentId, editDialog.value.form)
    ElMessage.success('更新成功')
    editDialog.value.visible = false
    fetchNotifications()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除通知「${row.title}」？`, '确认删除')
    await deleteAdminNotification(row.id)
    ElMessage.success('删除成功')
    fetchNotifications()
  } catch { /* ignore */ }
}

onMounted(fetchNotifications)
</script>

<style scoped>
.manage-container {
  max-width: 1100px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-wrap {
  margin-top: 20px;
  text-align: center;
}
</style>
