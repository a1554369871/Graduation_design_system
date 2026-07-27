<template>
  <div class="notifications-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>通告管理</span>
          <el-radio-group v-model="noticeType" size="small" @change="fetchNotifications">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="admin">通知</el-radio-button>
            <el-radio-button value="teacher">指导通知</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <div v-if="loading" style="text-align:center;padding:40px">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
      </div>

      <el-empty v-else-if="notifications.length === 0" description="暂无通知" />

      <div v-else class="notification-list">
        <div
          v-for="item in notifications"
          :key="item.id"
          class="notification-item"
          :class="{ unread: !item.is_read }"
          @click="handleRead(item)"
        >
          <div class="item-header">
            <el-tag :type="item.notice_type === 'admin' ? '' : 'warning'" size="small">
              {{ item.notice_type === 'admin' ? '通知' : '指导通知' }}
            </el-tag>
            <span class="sender">{{ item.sender_name }}</span>
            <span class="time">{{ formatTime(item.created_at) }}</span>
            <el-icon v-if="!item.is_read" class="unread-dot"><CircleCheckFilled /></el-icon>
          </div>
          <div class="item-title">{{ item.title }}</div>
          <div v-if="item.content" class="item-content">{{ item.content }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Loading, CircleCheckFilled } from '@element-plus/icons-vue'
import { getStudentNotifications, markNotificationRead } from '../../api/notification'

const noticeType = ref('all')
const notifications = ref([])
const loading = ref(false)

function formatTime(timeStr) {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function fetchNotifications() {
  loading.value = true
  try {
    const res = await getStudentNotifications({ type: noticeType.value })
    notifications.value = res
  } finally {
    loading.value = false
  }
}

async function handleRead(item) {
  if (!item.is_read) {
    try {
      await markNotificationRead(item.id)
      item.is_read = true
    } catch { /* ignore */ }
  }
}

onMounted(fetchNotifications)
</script>

<style scoped>
.notifications-container {
  max-width: 900px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.notification-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.notification-item {
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s;
}
.notification-item:hover {
  background: #f5f7fa;
}
.notification-item.unread {
  background: #ecf5ff;
  border-color: #b3d8ff;
}
.item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.sender {
  font-size: 13px;
  color: #909399;
}
.time {
  font-size: 12px;
  color: #c0c4cc;
  margin-left: auto;
}
.unread-dot {
  color: #409eff;
}
.item-title {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}
.item-content {
  margin-top: 6px;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>
