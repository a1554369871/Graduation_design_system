<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header"><span>项目管理</span><el-button type="primary" @click="openCreate">新建项目</el-button></div>
      </template>
      <el-form :inline="true" :model="query" size="small">
        <el-form-item label="关键词"><el-input v-model="query.keyword" placeholder="项目名称/学生姓名/学号" clearable style="width:240px" /></el-form-item>
        <el-form-item label="状态"><el-select v-model="query.status_id" placeholder="全部" clearable style="width:120px"><el-option v-for="s in statusDefs" :key="s.id" :label="s.name" :value="s.id" /></el-select></el-form-item>
        <el-form-item><el-button type="primary" @click="search">搜索</el-button><el-button @click="reset">重置</el-button></el-form-item>
      </el-form>
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="student_no" label="学号" width="100" />
        <el-table-column prop="student_name" label="学生" width="80" />
        <el-table-column prop="title" label="项目名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="advisor_name" label="指导教师" width="80" />
        <el-table-column prop="reviewer_name" label="评阅教师" width="80" />
        <el-table-column prop="status_name" label="状态" width="80">
          <template #default="{ row }"><el-tag :type="statusTagClass(row)" size="small">{{ row.status_name }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="submission_count" label="提交次数" width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" @click="showInteractions(row)">交互</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference><el-button size="small" type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > 0" background layout="prev,pager,next,total" :total="total" :page-size="query.per_page" :current-page="query.page" @current-change="page => { query.page = page; fetch() }" style="margin-top:16px;justify-content:center" />
    </el-card>

    <el-dialog v-model="formVisible" :title="isEdit ? '编辑项目' : '新建项目'" width="600px">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="学生" prop="student_id"><el-select v-model="form.student_id" filterable style="width:100%"><el-option v-for="s in studentList" :key="s.id" :label="`${s.student_id} - ${s.name}`" :value="s.id" /></el-select></el-form-item>
        <el-form-item label="项目名称" prop="title"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="毕设年份" prop="graduation_year_id"><el-select v-model="form.graduation_year_id" style="width:100%"><el-option v-for="y in years" :key="y.id" :label="y.year" :value="y.id" /></el-select></el-form-item>
        <el-form-item label="指导教师" prop="advisor_id"><el-select v-model="form.advisor_id" filterable style="width:100%"><el-option v-for="t in teacherList" :key="t.id" :label="`${t.teacher_id} - ${t.name}`" :value="t.id" /></el-select></el-form-item>
        <el-form-item label="评阅教师"><el-select v-model="form.reviewer_id" filterable clearable style="width:100%"><el-option v-for="t in teacherList" :key="t.id" :label="`${t.teacher_id} - ${t.name}`" :value="t.id" /></el-select></el-form-item>
        <el-form-item label="当前状态"><el-select v-model="form.current_status_id" style="width:100%"><el-option v-for="s in statusDefs" :key="s.id" :label="s.name" :value="s.id" /></el-select></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="最大提交次数"><el-input-number v-model="form.max_submissions" :min="1" :max="20" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="interactionVisible" title="交互过程" width="700px">
      <el-timeline v-if="interactions.length">
        <el-timeline-item v-for="(item, i) in interactions" :key="i" :timestamp="item.time" :type="item.type === 'review' ? 'success' : item.type === 'submission' ? 'primary' : 'info'">
          <div v-if="item.type === 'status_change'">
            <b>状态变更</b>：{{ item.content }}（{{ item.operator_role }}）
          </div>
          <div v-else-if="item.type === 'submission'">
            <b>提交</b>：v{{ item.version }} [{{ item.submission_type }}] {{ item.file_name }}
          </div>
          <div v-else-if="item.type === 'review'">
            <b>评审</b>：{{ item.reviewer_name }} {{ item.is_approved ? '✅通过' : '❌需修改' }}
            <span v-if="item.score"> 得分：{{ item.score }}</span>
            <p v-if="item.comment" style="color:#666;font-size:13px">{{ item.comment }}</p>
          </div>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无交互记录" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getProjects, createProject, updateProject, deleteProject, getInteractions } from '../../api/admin'
import { getTeacherList, getStudentList, getStatusDefs, getGraduationYears } from '../../api/admin'

const list = ref([]); const total = ref(0); const loading = ref(false)
const teacherList = ref([]); const studentList = ref([]); const statusDefs = ref([]); const years = ref([])
const formVisible = ref(false); const isEdit = ref(false); const submitLoading = ref(false)
const formRef = ref(null); const interactionVisible = ref(false); const interactions = ref([])

const query = reactive({ keyword: '', status_id: '', page: 1, per_page: 20 })
const form = reactive({ student_id: '', title: '', graduation_year_id: '', advisor_id: '', reviewer_id: '', current_status_id: 1, description: '', max_submissions: 5 })
const formRules = { student_id: [{ required: true, message: '必选' }], title: [{ required: true, message: '必填' }], graduation_year_id: [{ required: true, message: '必选' }], advisor_id: [{ required: true, message: '必选' }] }

function statusTagClass(row) { return '' }

async function fetch() {
  loading.value = true
  try {
    const res = await getProjects(query)
    list.value = res.items; total.value = res.total
  } finally { loading.value = false }
}

async function loadOptions() {
  teacherList.value = await getTeacherList()
  studentList.value = await getStudentList()
  statusDefs.value = await getStatusDefs()
  years.value = await getGraduationYears()
}

function search() { query.page = 1; fetch() }
function reset() { query.keyword = ''; query.status_id = ''; query.page = 1; fetch() }
function openCreate() { isEdit.value = false; Object.assign(form, { student_id: '', title: '', graduation_year_id: years.value[0]?.id || '', advisor_id: '', reviewer_id: '', current_status_id: statusDefs.value[0]?.id || 1, description: '', max_submissions: 5 }); formVisible.value = true }
function openEdit(row) { isEdit.value = true; Object.assign(form, row); formVisible.value = true }

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    if (isEdit.value) { await updateProject(form.id, form) } else { await createProject(form) }
    formVisible.value = false; fetch()
  } finally { submitLoading.value = false }
}

async function handleDelete(id) { await deleteProject(id); fetch() }

async function showInteractions(row) {
  interactions.value = await getInteractions(row.id)
  interactionVisible.value = true
}

onMounted(() => { loadOptions(); fetch() })
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
