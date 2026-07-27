<template>
  <div class="notifications-container">
    <el-card>
      <template #header>
        <span>通知（管理员）</span>
      </template>

      <div v-if="loading" style="text-align:center;padding:40px">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
      </div>

      <el-empty v-else-if="notifications.length === 0" description="暂无通知" />

      <div v-else class="notification-list">
        <div v-for="item in notifications" :key="item.id" class="notification-item">
          <div class="item-header">
            <el-tag size="small">通知</el-tag>
            <span class="sender">{{ item.sender_name }}</span>
            <span class="time">{{ formatTime(item.created_at) }}</span>
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
import { Loading } from '@element-plus/icons-vue'
import { getAdminNotifications } from '../../api/notification'

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
    const res = await getAdminNotifications()
    notifications.value = res
  } finally {
    loading.value = false
  }
}

onMounted(fetchNotifications)
</script>

<style scoped>
.notifications-container {
  max-width: 900px;
  margin: 0 auto;
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
}
.notification-item:hover {
  background: #f5f7fa;
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
