<template>
  <el-card>
    <template #header><span>评审历史</span></template>
    <el-table :data="list" border stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="50" />
      <el-table-column prop="student_name" label="学生" width="80" />
      <el-table-column prop="project_title" label="项目名称" min-width="200" show-overflow-tooltip />
      <el-table-column label="版本" width="60"><template #default="{ row }">v{{ row.version }}</template></el-table-column>
      <el-table-column prop="review_type" label="评审类型" width="80">
        <template #default="{ row }"><el-tag :type="row.review_type === 'advisor' ? '' : 'warning'" size="small">{{ row.review_type === 'advisor' ? '指导' : '评阅' }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="score" label="评分" width="60" />
      <el-table-column prop="is_approved" label="结果" width="60">
        <template #default="{ row }"><el-tag :type="row.is_approved ? 'success' : 'danger'" size="small">{{ row.is_approved ? '通过' : '需修改' }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="comment" label="意见" min-width="200" show-overflow-tooltip />
      <el-table-column prop="created_at" label="评审时间" width="170" />
    </el-table>
    <el-pagination v-if="total > 0" background layout="prev,pager,next,total" :total="total" :current-page="page" :page-size="20" @current-change="p => { page = p; fetch() }" style="margin-top:16px;justify-content:center" />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getReviewHistory } from '../../api/teacher'

const list = ref([]); const total = ref(0); const page = ref(1); const loading = ref(false)

async function fetch() {
  loading.value = true
  try { const res = await getReviewHistory({ page: page.value, per_page: 20 }); list.value = res.items; total.value = res.total } finally { loading.value = false }
}
onMounted(fetch)
</script>
