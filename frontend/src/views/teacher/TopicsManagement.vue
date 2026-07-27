<template>
  <div>
    <el-card shadow="hover" style="margin-bottom:16px">
      <template #header>
        <div class="card-header">
          <span>我的选题</span>
          <el-button type="primary" @click="dialogVisible = true">发布选题</el-button>
        </div>
      </template>
      <el-table :data="topics" border stripe v-loading="loading">
        <el-table-column prop="title" label="选题名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column label="已选/最大" width="100" align="center">
          <template #default="{ row }">{{ row.selected_count }} / {{ row.max_students }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '关闭' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" :type="row.is_active ? 'warning' : 'success'" @click="handleToggle(row)">
              {{ row.is_active ? '关闭' : '启用' }}
            </el-button>
            <el-popconfirm title="确定删除该选题？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑选题' : '发布选题'" width="600px">
      <el-form label-width="80px">
        <el-form-item label="选题名称" required>
          <el-input v-model="form.title" placeholder="请输入选题名称" />
        </el-form-item>
        <el-form-item label="选题描述">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请描述选题内容" />
        </el-form-item>
        <el-form-item label="最大人数">
          <el-input-number v-model="form.max_students" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">{{ editingId ? '保存' : '发布' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMyTopics, createTopic, updateTopic, deleteTopic } from '../../api/topic'

const topics = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const editingId = ref(null)
const form = ref({ title: '', description: '', max_students: 1 })

async function fetchData() {
  loading.value = true
  try {
    topics.value = await getMyTopics()
  } finally {
    loading.value = false
  }
}

function handleEdit(row) {
  editingId.value = row.id
  form.value = { title: row.title, description: row.description || '', max_students: row.max_students }
  dialogVisible.value = true
}

async function handleToggle(row) {
  try {
    await updateTopic(row.id, { is_active: !row.is_active })
    fetchData()
  } catch { /* handled by interceptor */ }
}

async function handleDelete(id) {
  try {
    await deleteTopic(id)
    fetchData()
  } catch { /* handled by interceptor */ }
}

async function handleSave() {
  if (!form.value.title) return
  saving.value = true
  try {
    if (editingId.value) {
      await updateTopic(editingId.value, form.value)
    } else {
      await createTopic(form.value)
    }
    dialogVisible.value = false
    editingId.value = null
    form.value = { title: '', description: '', max_students: 1 }
    fetchData()
  } finally {
    saving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
