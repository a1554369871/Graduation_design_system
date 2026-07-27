<template>
  <div class="progress-container">
    <el-row :gutter="16">
      <el-col :span="14">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>学生论文进度</span>
              <el-input
                v-model="keyword"
                placeholder="搜索学生姓名/学号/题目"
                clearable
                size="small"
                style="width:240px"
                @input="fetchStudents"
              />
            </div>
          </template>

          <div v-if="loading" style="text-align:center;padding:40px">
            <el-icon class="is-loading" :size="24"><Loading /></el-icon>
          </div>

          <el-empty v-else-if="students.length === 0" description="暂无指导学生" />

          <el-table v-else :data="students" stripe @row-click="handleRowClick">
            <el-table-column prop="student_no" label="学号" width="120" />
            <el-table-column prop="student_name" label="姓名" width="100" />
            <el-table-column prop="project_title" label="题目" min-width="180" show-overflow-tooltip />
            <el-table-column prop="status_name" label="当前进度" width="140">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status_sort)" size="small">
                  {{ row.status_name }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click.stop="openSendDialog(row)">
                  发送通知
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>发送通知记录</span>
            </div>
          </template>

          <div v-if="sentLoading" style="text-align:center;padding:20px">
            <el-icon class="is-loading" :size="20"><Loading /></el-icon>
          </div>

          <el-empty v-else-if="sentNotifications.length === 0" description="暂无发送记录" />

          <div v-else class="sent-list">
            <div v-for="item in sentNotifications" :key="item.id" class="sent-item">
              <div class="sent-header">
                <span class="sent-title">{{ item.title }}</span>
                <span class="sent-time">{{ formatTime(item.created_at) }}</span>
              </div>
              <div class="sent-meta">
                已读 {{ item.read_count }}/{{ item.recipient_count }} 人
              </div>
              <div v-if="item.content" class="sent-content">{{ item.content }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="sendDialog.visible" title="发送指导通知" width="500px">
      <el-form label-width="80px">
        <el-form-item label="接收学生">
          <el-select
            v-model="sendDialog.studentIds"
            multiple
            filterable
            placeholder="选择学生（可多选）"
            style="width:100%"
          >
            <el-option
              v-for="s in students"
              :key="s.student_id"
              :label="`${s.student_name} (${s.student_no})`"
              :value="s.student_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="sendDialog.title" placeholder="请输入通知标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="sendDialog.content"
            type="textarea"
            :rows="4"
            placeholder="请输入通知内容（选填）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sendDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="sending" @click="handleSend">发送</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import {
  getTeacherStudentsProgress,
  getTeacherSentNotifications,
  sendTeacherNotification,
} from '../../api/notification'

const students = ref([])
const keyword = ref('')
const loading = ref(false)
const sentNotifications = ref([])
const sentLoading = ref(false)
const sending = ref(false)

const sendDialog = ref({
  visible: false,
  studentIds: [],
  title: '',
  content: '',
})

function formatTime(timeStr) {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function getStatusTagType(sortOrder) {
  if (!sortOrder) return 'info'
  if (sortOrder <= 3) return 'danger'
  if (sortOrder <= 6) return 'warning'
  return 'success'
}

async function fetchStudents() {
  loading.value = true
  try {
    const res = await getTeacherStudentsProgress({ keyword: keyword.value })
    students.value = res
  } finally {
    loading.value = false
  }
}

async function fetchSentNotifications() {
  sentLoading.value = true
  try {
    const res = await getTeacherSentNotifications()
    sentNotifications.value = res
  } finally {
    sentLoading.value = false
  }
}

function openSendDialog(row) {
  sendDialog.value = {
    visible: true,
    studentIds: [row.student_id],
    title: '',
    content: '',
  }
}

function handleRowClick(row) {
  openSendDialog(row)
}

async function handleSend() {
  if (!sendDialog.value.title) {
    ElMessage.warning('请输入标题')
    return
  }
  if (sendDialog.value.studentIds.length === 0) {
    ElMessage.warning('请选择至少一个学生')
    return
  }
  sending.value = true
  try {
    await sendTeacherNotification({
      title: sendDialog.value.title,
      content: sendDialog.value.content,
      student_ids: sendDialog.value.studentIds,
    })
    ElMessage.success('发送成功')
    sendDialog.value.visible = false
    fetchSentNotifications()
  } finally {
    sending.value = false
  }
}

onMounted(() => {
  fetchStudents()
  fetchSentNotifications()
})
</script>

<style scoped>
.progress-container {
  max-width: 1200px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sent-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 600px;
  overflow-y: auto;
}
.sent-item {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #eee;
}
.sent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.sent-title {
  font-weight: 500;
  font-size: 14px;
}
.sent-time {
  font-size: 12px;
  color: #c0c4cc;
}
.sent-meta {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}
.sent-content {
  font-size: 13px;
  color: #606266;
  white-space: pre-wrap;
}
</style>
