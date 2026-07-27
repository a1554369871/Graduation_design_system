<template>
  <el-card>
    <template #header><div class="card-header"><span>毕设年份管理</span><el-button type="primary" @click="openCreate">新建年份</el-button></div></template>
    <el-table :data="list" border stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="year" label="年份" width="160" />
      <el-table-column prop="is_active" label="启用" width="70">
        <template #default="{ row }"><el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '是' : '否' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)"><template #reference><el-button size="small" type="danger">删除</el-button></template></el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑年份' : '新建年份'" width="400px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="年份" prop="year"><el-input v-model="form.year" placeholder="如 2025-2026" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getGraduationYears, createGraduationYear, updateGraduationYear, deleteGraduationYear } from '../../api/admin'

const list = ref([]); const loading = ref(false)
const dialogVisible = ref(false); const isEdit = ref(false); const submitLoading = ref(false)
const formRef = ref(null)
const form = reactive({ year: '', is_active: true })
const rules = { year: [{ required: true, message: '请输入年份' }] }

async function fetch() { loading.value = true; try { list.value = await getGraduationYears() } finally { loading.value = false } }
function openCreate() { isEdit.value = false; form.year = ''; form.is_active = true; dialogVisible.value = true }
function openEdit(row) { isEdit.value = true; form.id = row.id; form.year = row.year; form.is_active = row.is_active; dialogVisible.value = true }
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false); if (!valid) return
  submitLoading.value = true
  try {
    if (isEdit.value) { await updateGraduationYear(form.id, { year: form.year, is_active: form.is_active }) } else { await createGraduationYear({ year: form.year }) }
    dialogVisible.value = false; fetch()
  } finally { submitLoading.value = false }
}
async function handleDelete(id) { await deleteGraduationYear(id); fetch() }
onMounted(fetch)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; }
</style>
