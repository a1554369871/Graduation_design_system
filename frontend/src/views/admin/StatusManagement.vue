<template>
  <el-card>
    <template #header><div class="card-header"><span>毕设状态管理</span><el-button type="primary" @click="openCreate">新建状态</el-button></div></template>
    <el-table :data="list" border stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" width="120" />
      <el-table-column prop="code" label="代码标识" width="140" />
      <el-table-column prop="sort_order" label="排序" width="70" />
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑状态' : '新建状态'" width="400px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="代码" prop="code"><el-input v-model="form.code" :disabled="isEdit" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
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
import { getStatusDefs, createStatusDef, updateStatusDef, deleteStatusDef } from '../../api/admin'

const list = ref([]); const loading = ref(false)
const dialogVisible = ref(false); const isEdit = ref(false); const submitLoading = ref(false)
const formRef = ref(null)
const form = reactive({ name: '', code: '', sort_order: 0, is_active: true })
const rules = { name: [{ required: true }], code: [{ required: true }] }

async function fetch() { loading.value = true; try { list.value = await getStatusDefs() } finally { loading.value = false } }
function openCreate() { isEdit.value = false; Object.assign(form, { name: '', code: '', sort_order: 0, is_active: true }); dialogVisible.value = true }
function openEdit(row) { isEdit.value = true; Object.assign(form, row); dialogVisible.value = true }
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    if (isEdit.value) { await updateStatusDef(form.id, form) } else { await createStatusDef(form) }
    dialogVisible.value = false; fetch()
  } finally { submitLoading.value = false }
}
async function handleDelete(id) { await deleteStatusDef(id); fetch() }

onMounted(fetch)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; }
</style>
