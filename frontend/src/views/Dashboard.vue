<template>
  <div class="dashboard">
    <h2>欢迎，{{ auth.userName }}</h2>
    <p style="color:#999;margin-bottom:24px">{{ roleText }}，请从左侧菜单选择功能</p>

    <div v-if="auth.isAdmin" class="stats">
      <el-row :gutter="16">
        <el-col :span="6"><el-card shadow="hover"><StatCard icon="User" label="学生总数" :value="stats.total_students" color="#409eff" /></el-card></el-col>
        <el-col :span="6"><el-card shadow="hover"><StatCard icon="Avatar" label="教师总数" :value="stats.total_teachers" color="#67c23a" /></el-card></el-col>
        <el-col :span="6"><el-card shadow="hover"><StatCard icon="FolderOpened" label="项目总数" :value="stats.total_projects" color="#e6a23c" /></el-card></el-col>
        <el-col :span="6"><el-card shadow="hover"><StatCard icon="Upload" label="提交总数" :value="stats.total_submissions" color="#f56c6c" /></el-card></el-col>
      </el-row>
      <el-card shadow="hover" style="margin-top:16px">
        <template #header><span>项目状态分布</span></template>
        <div v-if="stats.status_stats?.length">
          <div v-for="s in stats.status_stats" :key="s.name" class="status-bar">
            <span class="status-label">{{ s.name }}</span>
            <el-progress :percentage="statusPercent(s.count)" :stroke-width="20" striped />
          </div>
        </div>
        <el-empty v-else description="暂无数据" />
      </el-card>
    </div>

    <div v-if="auth.isStudent">
      <el-card shadow="hover">
        <template #header><span>我的毕设概览</span></template>
        <el-skeleton :loading="loading" animated>
          <div v-if="myProject">
            <p><b>项目名称：</b>{{ myProject.title }}</p>
            <p><b>当前状态：</b><el-tag :type="statusTagType">{{ myProject.status_name }}</el-tag></p>
            <p><b>指导老师：</b>{{ myProject.advisor_name }}</p>
            <p><b>评阅老师：</b>{{ myProject.reviewer_name }}</p>
            <p><b>毕设年份：</b>{{ myProject.year }}</p>
            <p><b>已提交次数：</b>{{ myProject.submission_count }} / {{ myProject.max_submissions }}</p>
          </div>
        </el-skeleton>
      </el-card>
    </div>

    <div v-if="auth.isTeacher">
      <el-row :gutter="16">
        <el-col :span="12"><el-card shadow="hover">
          <template #header><el-icon><User /></el-icon> 我的指导学生</template>
          <el-skeleton :loading="loading" animated>
            <div v-if="advisees.length">
              <p v-for="s in advisees" :key="s.id">{{ s.student_name }} - {{ s.status_name }}</p>
            </div>
          </el-skeleton>
        </el-card></el-col>
        <el-col :span="12"><el-card shadow="hover">
          <template #header><el-icon><EditPen /></el-icon> 待评审</template>
          <el-skeleton :loading="loading" animated>
            <div v-if="pendings.length">
              <p v-for="p in pendings" :key="p.submission?.id">{{ p.project.student_name }} - v{{ p.submission.version }}</p>
            </div>
          </el-skeleton>
        </el-card></el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { getDashboard } from '../api/admin'
import { getMyStudents, getPendingReviews } from '../api/teacher'
import { getMyProject } from '../api/student'

const auth = useAuthStore()
const loading = ref(false)
const stats = ref({})
const myProject = ref(null)
const advisees = ref([])
const pendings = ref([])

const roleText = computed(() => {
  if (auth.isAdmin) return '管理员'
  if (auth.isTeacher) return '教师'
  return '学生'
})

const statusTagType = computed(() => {
  if (!myProject.value) return ''
  const map = { topic_selection: 'info', first_draft: '', round1: 'warning', round2: 'warning', round3: 'danger', final_check: 'success', final_submission: 'success', defense: 'success', archived: 'info' }
  const code = myProject.value.status_code
  return map[code] || ''
})

function statusPercent(count) {
  const total = stats.value.total_projects || 1
  return Math.round((count / total) * 100)
}

onMounted(async () => {
  loading.value = true
  try {
    if (auth.isAdmin) {
      stats.value = await getDashboard()
    } else if (auth.isStudent) {
      try { myProject.value = await getMyProject() } catch { myProject.value = null }
    } else if (auth.isTeacher) {
      advisees.value = await getMyStudents({ type: 'advisor' })
      pendings.value = await getPendingReviews({ type: 'advisor' })
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard { padding: 8px; }
.stats { margin-top: 16px; }
.status-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.status-label { width: 60px; font-size: 14px; flex-shrink: 0; }
</style>
