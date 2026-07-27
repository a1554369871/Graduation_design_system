<template>
  <div>
    <el-card shadow="hover" style="margin-bottom:16px">
      <template #header><span>待审核选题</span></template>
      <el-table :data="pendingList" border stripe v-loading="loading">
        <el-table-column prop="student_name" label="学生姓名" width="120" />
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="title" label="选题名称" min-width="200" />
        <el-table-column prop="description" label="选题描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.type === 'select' ? '' : 'warning'" size="small">
              {{ row.type === 'select' ? '选择选题' : '自主选题' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <el-button type="success" size="small" @click="handleReview(row, 'approve')">通过</el-button>
            <el-button type="danger" size="small" @click="handleReview(row, 'reject')">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && pendingList.length === 0" description="暂无待审核的选题" />
    </el-card>

    <el-card shadow="hover">
      <template #header><span>审核历史</span></template>
      <el-table :data="reviewedList" border stripe>
        <el-table-column prop="student_name" label="学生姓名" width="120" />
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="title" label="选题名称" min-width="200" />
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.type === 'select' ? '' : 'warning'" size="small">
              {{ row.type === 'select' ? '选择选题' : '自主选题' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="审核结果" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'approved' ? 'success' : 'danger'" size="small">
              {{ row.status === 'approved' ? '通过' : '驳回' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="review_comment" label="审核意见" min-width="200" show-overflow-tooltip />
        <el-table-column prop="updated_at" label="审核时间" width="170" />
      </el-table>
      <el-empty v-if="reviewedList.length === 0" description="暂无审核记录" />
    </el-card>

    <el-dialog v-model="rejectDialog" title="驳回选题" width="450px">
      <el-form label-width="80px">
        <el-form-item label="驳回原因">
          <el-input v-model="rejectComment" type="textarea" :rows="3" placeholder="请输入驳回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAllPendingSelections, reviewSelection, getReviewedSelections } from '../../api/topic'

const loading = ref(false)
const pendingList = ref([])
const reviewedList = ref([])
const rejectDialog = ref(false)
const rejectComment = ref('')
const currentSelection = ref(null)

async function fetchData() {
  loading.value = true
  try {
    const [pending, reviewed] = await Promise.all([
      getAllPendingSelections(),
      getReviewedSelections(),
    ])
    pendingList.value = pending
    reviewedList.value = reviewed
  } finally {
    loading.value = false
  }
}

function handleReview(row, action) {
  currentSelection.value = row
  if (action === 'approve') {
    reviewSelection(row.id, { action: 'approve', comment: '' })
      .then(() => fetchData())
      .catch(() => {})
  } else {
    rejectComment.value = ''
    rejectDialog.value = true
  }
}

async function confirmReject() {
  try {
    await reviewSelection(currentSelection.value.id, {
      action: 'reject',
      comment: rejectComment.value,
    })
    rejectDialog.value = false
    currentSelection.value = null
    fetchData()
  } catch { /* handled by interceptor */ }
}

onMounted(fetchData)
</script>
