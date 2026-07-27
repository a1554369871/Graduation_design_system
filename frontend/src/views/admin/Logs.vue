<template>
  <el-card>
    <template #header><span>操作日志</span></template>
    <el-table :data="list" border stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="50" />
      <el-table-column prop="username" label="操作者" width="100" />
      <el-table-column prop="action" label="操作" width="120" />
      <el-table-column prop="target_type" label="对象类型" width="100" />
      <el-table-column prop="target_id" label="对象ID" width="70" />
      <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
      <el-table-column prop="ip_address" label="IP" width="130" />
      <el-table-column prop="created_at" label="时间" width="170" />
    </el-table>
    <el-pagination v-if="total > 0" background layout="prev,pager,next,total" :total="total" :current-page="page" :page-size="20" @current-change="p => { page = p; fetch() }" style="margin-top:16px;justify-content:center" />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLogs } from '../../api/admin'

const list = ref([]); const total = ref(0); const page = ref(1); const loading = ref(false)

async function fetch() {
  loading.value = true
  try { const res = await getLogs({ page: page.value, per_page: 20 }); list.value = res.items; total.value = res.total } finally { loading.value = false }
}
onMounted(fetch)
</script>
