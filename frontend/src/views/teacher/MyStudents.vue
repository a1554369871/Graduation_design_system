<template>
  <div>
    <el-card>
      <template #header><div class="card-header"><span>我的学生</span></div></template>
      <el-radio-group v-model="reviewType" style="margin-bottom:16px">
        <el-radio-button value="advisor">指导学生</el-radio-button>
        <el-radio-button value="reviewer">评阅学生</el-radio-button>
      </el-radio-group>
      <el-form :inline="true" size="small">
        <el-form-item><el-input v-model="keyword" placeholder="学生姓名/学号/项目名称" clearable style="width:280px" @keyup.enter="search" /></el-form-item>
        <el-form-item><el-button type="primary" @click="search">搜索</el-button></el-form-item>
      </el-form>
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="student_no" label="学号" width="100" />
        <el-table-column prop="student_name" label="姓名" width="80" />
        <el-table-column prop="student_department" label="院系" width="120" />
        <el-table-column prop="title" label="项目名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status_name" label="状态" width="80">
          <template #default="{ row }"><el-tag size="small">{{ row.status_name }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="submission_count" label="提交次数" width="80" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewProject(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer v-model="drawerVisible" :title="`项目详情 - ${currentProject?.student_name || ''}`" size="50%">
      <template v-if="currentProject">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="项目名称">{{ currentProject.title }}</el-descriptions-item>
          <el-descriptions-item label="当前状态">{{ currentProject.status_name }}</el-descriptions-item>
          <el-descriptions-item label="指导教师">{{ currentProject.advisor_name }}</el-descriptions-item>
          <el-descriptions-item label="评阅教师">{{ currentProject.reviewer_name }}</el-descriptions-item>
          <el-descriptions-item label="毕设年份">{{ currentProject.year }}</el-descriptions-item>
          <el-descriptions-item label="提交次数">{{ currentProject.submission_count }}/{{ currentProject.max_submissions }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="reviewType === 'advisor'" style="margin:12px 0;text-align:right">
          <el-button type="warning" :loading="advancing" @click="handleAdvanceStage">推进阶段</el-button>
          <span style="font-size:12px;color:#999;margin-left:8px">手动将学生推进到下一阶段</span>
        </div>

        <el-divider>提交与评审记录</el-divider>
        <div v-for="sub in currentProject.submissions" :key="sub.id" style="margin-bottom:12px">
          <el-card shadow="hover" size="small">
            <div>
              <el-tag size="small" :type="subTagType(sub.submission_type)" style="margin-right:8px">{{ subTypeLabel(sub.submission_type) }}</el-tag>
              v{{ sub.version }} - {{ sub.file_name }}
              <el-button type="primary" size="small" link style="margin-left:8px" @click="handleDownload(sub)">下载</el-button>
              <span style="color:#999;margin-left:12px">{{ sub.created_at }}</span>
            </div>
            <div v-for="rv in sub.reviews" :key="rv.id" style="margin-top:8px;padding:8px;background:#f6f6f6;border-radius:4px">
              <el-tag size="small" :type="rv.review_type === 'advisor' ? '' : 'warning'" style="margin-right:8px">{{ rv.review_type === 'advisor' ? '导师' : '评阅' }}</el-tag>
              {{ rv.reviewer_name }} ·
              <span v-if="rv.score">评分：{{ rv.score }} · </span>
              <el-tag :type="rv.is_approved ? 'success' : 'danger'" size="mini">{{ rv.is_approved ? '通过' : '需修改' }}</el-tag>
              <p v-if="rv.comment" style="margin:4px 0 0;color:#666;font-size:13px">{{ rv.comment }}</p>
            </div>
          </el-card>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMyStudents, getProjectDetail, advanceStage, downloadSubmission } from '../../api/teacher'

const list = ref([]); const loading = ref(false)
const reviewType = ref('advisor'); const keyword = ref('')
const drawerVisible = ref(false); const currentProject = ref(null)
const advancing = ref(false)

function subTagType(t) { return { draft: '', revision: 'warning', final: 'success' }[t] || '' }
function subTypeLabel(t) { return { draft: '初稿', revision: '修改稿', final: '最终版' }[t] || t }

async function fetch() {
  loading.value = true
  try { list.value = await getMyStudents({ type: reviewType.value, keyword: keyword.value }) } finally { loading.value = false }
}

function search() { fetch() }

async function viewProject(row) {
  const detail = await getProjectDetail(row.id)
  currentProject.value = detail
  drawerVisible.value = true
}

async function handleAdvanceStage() {
  if (!currentProject.value) return
  advancing.value = true
  try {
    const res = await advanceStage(currentProject.value.id)
    ElMessage.success(res.msg)
    await viewProject({ id: currentProject.value.id })
  } catch {
    // handled by interceptor
  } finally {
    advancing.value = false
  }
}

async function handleDownload(submission) {
  try {
    const blob = await downloadSubmission(submission.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = submission.file_name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch {}
}

watch(reviewType, () => fetch())
onMounted(fetch)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; }
</style>
