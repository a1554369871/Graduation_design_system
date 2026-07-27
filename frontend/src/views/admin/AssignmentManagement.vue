<template>
  <div>
    <el-card>
      <template #header><div class="card-header"><span>教师分配</span></div></template>
      <el-form :inline="true" size="small">
        <el-form-item label="教师">
          <el-select v-model="query.teacher_id" placeholder="全部" clearable style="width:180px">
            <el-option v-for="t in teacherList" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="search">搜索</el-button><el-button @click="reset">重置</el-button></el-form-item>
      </el-form>
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="student_no" label="学号" width="100" />
        <el-table-column prop="student_name" label="学生姓名" width="100" />
        <el-table-column prop="title" label="项目名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="advisor_name" label="指导教师" width="100" />
        <el-table-column prop="reviewer_name" label="评阅教师" width="100" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="assignAdvisor(row)">分配导师</el-button>
            <el-button size="small" @click="assignReviewer(row)">分配评阅</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > 0" background layout="prev,pager,next,total" :total="total" :page-size="query.per_page" :current-page="query.page" @current-change="page => { query.page = page; fetch() }" style="margin-top:16px;justify-content:center" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="assignTitle" width="400px">
      <el-form label-width="80px">
        <el-form-item label="选择教师">
          <el-select v-model="selectedTeacherId" filterable style="width:100%">
            <el-option v-for="t in teacherList" :key="t.id" :label="`${t.teacher_id} - ${t.name} (${t.title || ''})`" :value="t.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleAssign">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getAssignments, assignAdvisor as apiAssignAdvisor, assignReviewer as apiAssignReviewer, getTeacherList } from '../../api/admin'

const list = ref([]); const total = ref(0); const loading = ref(false)
const teacherList = ref([]); const dialogVisible = ref(false); const submitLoading = ref(false)
const selectedTeacherId = ref(null); const currentRow = ref(null); const assignType = ref('advisor')
const query = reactive({ teacher_id: '', page: 1, per_page: 20 })
const assignTitle = computed(() => assignType.value === 'advisor' ? '分配指导教师' : '分配评阅教师')

async function fetch() {
  loading.value = true
  try { const res = await getAssignments(query); list.value = res.items; total.value = res.total } finally { loading.value = false }
}

function search() { query.page = 1; fetch() }
function reset() { query.teacher_id = ''; query.page = 1; fetch() }

async function assignAdvisor(row) {
  assignType.value = 'advisor'; currentRow.value = row; selectedTeacherId.value = null; dialogVisible.value = true
}
async function assignReviewer(row) {
  assignType.value = 'reviewer'; currentRow.value = row; selectedTeacherId.value = null; dialogVisible.value = true
}
async function handleAssign() {
  if (!selectedTeacherId.value) return
  submitLoading.value = true
  try {
    const data = { student_id: currentRow.value.student_id, teacher_id: selectedTeacherId.value }
    if (assignType.value === 'advisor') { await apiAssignAdvisor(data) } else { await apiAssignReviewer(data) }
    dialogVisible.value = false; fetch()
  } finally { submitLoading.value = false }
}

onMounted(async () => {
  teacherList.value = await getTeacherList(); fetch()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
