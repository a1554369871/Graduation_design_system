<template>
  <div>
    <el-card>
      <template #header><span>待评审</span></template>
      <el-radio-group v-model="reviewType" style="margin-bottom:16px">
        <el-radio-button value="advisor">指导评审</el-radio-button>
        <el-radio-button value="reviewer">评阅评审</el-radio-button>
      </el-radio-group>
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="project.student_no" label="学号" width="100" />
        <el-table-column prop="project.student_name" label="学生" width="80" />
        <el-table-column prop="project.title" label="项目名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="版本" width="60">
          <template #default="{ row }">v{{ row.submission.version }}</template>
        </el-table-column>
        <el-table-column label="类型" width="70">
          <template #default="{ row }">{{ subTypeLabel(row.submission.submission_type) }}</template>
        </el-table-column>
        <el-table-column prop="submission.file_name" label="文件名" min-width="180" show-overflow-tooltip />
        <el-table-column prop="submission.description" label="说明" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleDownload(row.submission)">下载</el-button>
            <el-button size="small" type="primary" @click="openReview(row)">评审</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="reviewVisible" title="提交评审" width="500px">
      <div v-if="currentItem">
        <p><b>学生：</b>{{ currentItem.project.student_name }} | <b>项目：</b>{{ currentItem.project.title }} | <b>版本：</b>v{{ currentItem.submission.version }}</p>
        <el-divider />
        <el-form label-width="80px">
          <el-form-item label="评分">
            <el-input-number v-model="reviewForm.score" :min="0" :max="100" :precision="1" />
          </el-form-item>
          <el-form-item label="评审意见">
            <el-input v-model="reviewForm.comment" type="textarea" :rows="4" placeholder="请填写评审意见" />
          </el-form-item>
          <el-form-item label="评审结果">
            <el-radio-group v-model="reviewForm.is_approved">
              <el-radio :value="true">通过</el-radio>
              <el-radio :value="false">需要修改</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">提交评审</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getPendingReviews, submitReview, downloadSubmission } from '../../api/teacher'

const list = ref([]); const loading = ref(false)
const reviewType = ref('advisor'); const reviewVisible = ref(false); const submitLoading = ref(false)
const currentItem = ref(null)
const reviewForm = ref({ score: 80, comment: '', is_approved: true, submission_id: null })

function subTypeLabel(t) { return { draft: '初稿', round1: '一轮', round2: '二轮', round3: '三轮', final_check: '查重定稿', final: '最终稿' }[t] || t }

async function fetch() {
  loading.value = true
  try { list.value = await getPendingReviews({ type: reviewType.value }) } finally { loading.value = false }
}

function openReview(row) {
  currentItem.value = row
  reviewForm.value = { score: 80, comment: '', is_approved: true, submission_id: row.submission.id }
  reviewVisible.value = true
}

async function handleSubmit() {
  submitLoading.value = true
  try {
    await submitReview({ ...reviewForm.value, review_type: reviewType.value })
    reviewVisible.value = false
    fetch()
  } finally { submitLoading.value = false }
}

async function handleDownload(submission) {
  try {
    const blob = await downloadSubmission(submission.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = submission.file_name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch { /* handled by interceptor */ }
}

watch(reviewType, () => fetch())
onMounted(fetch)
</script>
