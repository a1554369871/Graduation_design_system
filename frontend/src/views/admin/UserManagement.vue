<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="openCreate">新建用户</el-button>
        </div>
      </template>
      <el-form :inline="true" :model="query" size="small">
        <el-form-item label="角色"><el-select v-model="query.role" placeholder="全部" clearable style="width:120px"><el-option label="学生" value="student" /><el-option label="教师" value="teacher" /><el-option label="管理员" value="admin" /></el-select></el-form-item>
        <el-form-item label="关键词"><el-input v-model="query.keyword" placeholder="姓名/用户名" clearable /></el-form-item>
        <el-form-item><el-button type="primary" @click="search">搜索</el-button><el-button @click="reset">重置</el-button></el-form-item>
      </el-form>
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="role" label="角色" width="80">
          <template #default="{ row }"><el-tag :type="roleTag(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="student_id" label="学号/工号" width="120" />
        <el-table-column prop="department" label="院系" />
        <el-table-column prop="class_name" label="班级" width="100" />
        <el-table-column prop="title" label="职称" width="80" />
        <el-table-column prop="is_active" label="状态" width="70">
          <template #default="{ row }"><el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference><el-button size="small" type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > 0" background layout="prev,pager,next,total" :total="total" :page-size="query.per_page" :current-page="query.page" @current-change="page => { query.page = page; fetch() }" style="margin-top:16px;justify-content:center" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新建用户'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username"><el-input v-model="form.username" :disabled="isEdit" /></el-form-item>
        <el-form-item label="姓名" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="角色" prop="role"><el-select v-model="form.role" :disabled="isEdit" style="width:100%"><el-option label="学生" value="student" /><el-option label="教师" value="teacher" /><el-option label="管理员" value="admin" /></el-select></el-form-item>
        <el-form-item v-if="form.role === 'student'" label="学号" prop="student_id"><el-input v-model="form.student_id" /></el-form-item>
        <el-form-item v-if="form.role === 'teacher'" label="工号" prop="teacher_id"><el-input v-model="form.teacher_id" /></el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item v-if="form.role === 'student'" label="班级"><el-input v-model="form.class_name" /></el-form-item>
        <el-form-item label="院系"><el-input v-model="form.department" /></el-form-item>
        <el-form-item v-if="form.role === 'student'" label="专业"><el-input v-model="form.major" /></el-form-item>
        <el-form-item v-if="form.role === 'teacher'" label="职称"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item v-if="isEdit" label="启用"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getUsers, createUser, updateUser, deleteUser } from '../../api/admin'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const query = reactive({ role: '', keyword: '', page: 1, per_page: 20 })
const form = reactive({ username: '', name: '', role: 'student', student_id: '', teacher_id: '', password: '123456', class_name: '', department: '', major: '', title: '', email: '', phone: '', is_active: true })
const rules = { username: [{ required: true, message: '必填' }], name: [{ required: true, message: '必填' }], role: [{ required: true, message: '必填' }] }

function roleTag(role) { return { student: '', teacher: 'success', admin: 'danger' }[role] || '' }
function roleLabel(role) { return { student: '学生', teacher: '教师', admin: '管理员' }[role] || role }

async function fetch() {
  loading.value = true
  try {
    const res = await getUsers(query)
    list.value = res.items; total.value = res.total
  } finally { loading.value = false }
}

function search() { query.page = 1; fetch() }
function reset() { query.role = ''; query.keyword = ''; query.page = 1; fetch() }
function openCreate() {
  isEdit.value = false
  Object.assign(form, { username: '', name: '', role: 'student', student_id: '', teacher_id: '', password: '123456', class_name: '', department: '', major: '', title: '', email: '', phone: '', is_active: true })
  dialogVisible.value = true
}
function openEdit(row) {
  isEdit.value = true
  Object.assign(form, row)
  form.password = ''
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    if (isEdit.value) { await updateUser(form.id, form) } else { await createUser(form) }
    dialogVisible.value = false; fetch()
  } finally { submitLoading.value = false }
}

async function handleDelete(id) {
  await deleteUser(id); fetch()
}

onMounted(fetch)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
