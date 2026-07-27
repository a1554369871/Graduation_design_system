<template>
  <div>
    <el-card v-if="error" shadow="hover">
      <el-empty :description="error" />
    </el-card>
    <el-card v-else-if="!project" shadow="hover" v-loading="true">
      <div style="height:200px" />
    </el-card>
    <template v-else>
      <el-card shadow="hover" style="margin-bottom:16px">
        <template #header><span>查重定稿</span></template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">{{ project.title }}</el-descriptions-item>
          <el-descriptions-item label="指导老师">{{ project.advisor_name }}</el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag>{{ project.status_name }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="提交次数">{{ project.submission_count }} / {{ project.max_submissions }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
      <el-card v-if="stageStatus === 'locked'" shadow="hover">
        <el-alert type="info" show-icon :closable="false" title="查重定稿阶段未开启，请先完成论文修改审核。" />
      </el-card>
      <el-card v-else-if="stageStatus === 'approved'" shadow="hover">
        <el-alert type="success" show-icon :closable="false" title="查重定稿已通过评审，请进入最终稿阶段提交材料。" />
      </el-card>
      <el-card v-else-if="stageStatus === 'completed'" shadow="hover">
        <el-alert type="info" show-icon :closable="false" title="查重定稿阶段已完成，请进入最终稿阶段。" />
      </el-card>
      <el-card v-else shadow="hover" style="margin-bottom:16px">
        <template #header><span>提交查重定稿</span></template>
        <el-form label-width="80px" style="max-width:500px" @submit.prevent>
          <el-form-item label="说明">
            <el-input v-model="description" placeholder="可选的提交说明" />
          </el-form-item>
          <el-form-item label="文件">
            <el-upload ref="uploadRef" :auto-upload="false" :limit="1" accept=".pdf,.doc,.docx,.zip,.rar" :on-change="handleFileChange">
              <el-button type="primary">选择文件</el-button>
              <template #tip><p style="color:#999;font-size:12px">支持 pdf/doc/docx/zip/rar</p></template>
            </el-upload>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="submitting" @click="handleSubmit" :disabled="!selectedFile">提交查重定稿</el-button>
          </el-form-item>
        </el-form>
      </el-card>
      <el-card v-if="submissions.length > 0" shadow="hover">
        <template #header><span>历史提交记录</span></template>
        <el-timeline>
          <el-timeline-item v-for="sub in submissions" :key="sub.id" :timestamp="sub.created_at" placement="top">
            <el-card shadow="hover" size="small">
              <div>
                <el-tag size="small" style="margin-right:8px">v{{ sub.version }}</el-tag>
                {{ sub.file_name }}
                <el-button type="primary" size="small" link style="margin-left:8px" @click="handleDownload(sub)">下载</el-button>
                <span v-if="sub.downloaded_at" style="margin-left:12px;color:#67c23a">
                  ⬇ 已下载 {{ sub.download_count }} 次
                </span>
                <span v-else style="margin-left:12px;color:#999">未下载</span>
                <span v-if="sub.description" style="color:#999;margin-left:12px">{{ sub.description }}</span>
              </div>
              <div v-for="rv in sub.reviews" :key="rv.id" style="margin-top:8px;padding:8px;background:#f6f6f6;border-radius:4px">
                <el-tag size="small" style="margin-right:8px">{{ rv.reviewer_name }}</el-tag>
                <span v-if="rv.score">评分：{{ rv.score }} · </span>
                <el-tag :type="rv.is_approved ? 'success' : 'danger'" size="small">
                  {{ rv.is_approved ? '通过' : '需修改' }}
                </el-tag>
                <p v-if="rv.comment" style="margin:4px 0 0;color:#666;font-size:13px;white-space:pre-wrap">{{ rv.comment }}</p>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMyProject, submitPaper, downloadSubmission } from '../../api/student'

const project = ref(null)
const error = ref('')
const submitting = ref(false)
const stageStatus = ref('current')
const submissions = ref([])
const description = ref('')
const selectedFile = ref(null)
const uploadRef = ref(null)

const STAGE = 'final_check'
const STAGE_CODES = { topic_selection: 1, first_draft: 2, round1: 3, round2: 4, round3: 5, final_check: 6, final_submission: 7, defense: 8, archived: 9 }

function handleFileChange(file) { selectedFile.value = file.raw }

async function handleSubmit() {
  if (!selectedFile.value) return
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    fd.append('stage', STAGE)
    if (description.value) fd.append('description', description.value)
    await submitPaper(fd)
    description.value = ''
    selectedFile.value = null
    fetchData()
  } finally { submitting.value = false }
}

function getStageStatus() {
  const code = project.value?.status_code
  if (!code) return 'locked'
  const currentSort = STAGE_CODES[code] || 0
  const thisSort = STAGE_CODES[STAGE]
  if (currentSort > thisSort) return 'completed'
  if (currentSort < thisSort) return 'locked'
  const subs = submissions.value.filter(s => s.submission_type === STAGE)
  if (subs.length > 0) {
    const last = subs[subs.length - 1]
    if (last.reviews?.some(r => r.is_approved)) return 'approved'
  }
  return 'current'
}

async function fetchData() {
  try {
    const res = await getMyProject()
    project.value = res
    submissions.value = (res.submissions || []).filter(s => s.submission_type === STAGE)
    stageStatus.value = getStageStatus()
  } catch { error.value = '暂无毕设项目，请联系管理员' }
}

async function handleDownload(sub) {
  try {
    const res = await downloadSubmission(sub.id)
    const url = URL.createObjectURL(res)
    const a = document.createElement('a')
    a.href = url
    a.download = sub.file_name
    a.click()
    URL.revokeObjectURL(url)
  } catch {}
}

onMounted(fetchData)
</script>
