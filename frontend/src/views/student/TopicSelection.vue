<template>
  <div>
    <el-card v-if="error" shadow="hover">
      <el-empty :description="error" />
    </el-card>
    <el-card v-else-if="!loaded" shadow="hover" v-loading="true">
      <div style="height:200px" />
    </el-card>
    <template v-else>
      <el-card v-if="mySelection && mySelection.status === 'approved'" shadow="hover" style="margin-bottom:16px">
        <template #header><span>我的选题状态</span></template>
        <el-alert type="success" show-icon :closable="false">
          <template #title>
            选题已通过审核！选题：{{ mySelection.title }}，可进入论文管理提交初稿。
          </template>
        </el-alert>
      </el-card>
      <el-card v-if="mySelection && mySelection.status === 'pending'" shadow="hover" style="margin-bottom:16px">
        <template #header><span>我的选题状态</span></template>
        <el-alert type="warning" show-icon :closable="false">
          <template #title>
            选题申请已提交，等待教师审核。选题：{{ mySelection.title }}
          </template>
        </el-alert>
      </el-card>
      <el-card v-if="mySelection && mySelection.status === 'rejected'" shadow="hover" style="margin-bottom:16px">
        <template #header><span>我的选题状态</span></template>
        <el-alert type="error" show-icon :closable="false">
          <template #title>
            选题被驳回：{{ mySelection.review_comment || '未给出原因' }}，请重新选题。
          </template>
        </el-alert>
      </el-card>
      <el-card shadow="hover" v-if="!mySelection || mySelection.status === 'rejected'">
        <template #header>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="可选选题" name="available" />
            <el-tab-pane label="自主选题" name="propose" />
          </el-tabs>
        </template>
        <div v-if="activeTab === 'available'">
          <el-table :data="topics" border stripe v-loading="loading">
            <el-table-column prop="title" label="选题名称" min-width="200" />
            <el-table-column prop="teacher_name" label="发布教师" width="120" />
            <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
            <el-table-column label="已选/最大" width="100" align="center">
              <template #default="{ row }">{{ row.selected_count }} / {{ row.max_students }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  :disabled="!row.can_select"
                  @click="handleSelect(row)"
                >
                  {{ row.can_select ? '选择' : '已满' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && topics.length === 0" description="暂无可选选题" />
        </div>
        <div v-if="activeTab === 'propose'">
          <el-form label-width="80px" style="max-width:600px">
            <el-form-item label="选题标题" required>
              <el-input v-model="proposeForm.title" placeholder="请输入选题标题" />
            </el-form-item>
            <el-form-item label="选题描述">
              <el-input v-model="proposeForm.description" type="textarea" :rows="4" placeholder="请描述选题内容" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="proposeLoading" @click="handlePropose">提交审核</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAvailableTopics, getMySelection, selectTopic, proposeTopic } from '../../api/topic'

const loading = ref(false)
const proposeLoading = ref(false)
const topics = ref([])
const mySelection = ref(null)
const activeTab = ref('available')
const proposeForm = ref({ title: '', description: '' })
const error = ref('')
const loaded = ref(false)

async function fetchData() {
  loading.value = true
  try {
    const [topicsRes, selectionRes] = await Promise.all([
      getAvailableTopics(),
      getMySelection(),
    ])
    topics.value = topicsRes
    mySelection.value = selectionRes
    loaded.value = true
  } catch {
    error.value = '暂无可选选题'
  } finally {
    loading.value = false
  }
}

async function handleSelect(topic) {
  try {
    await selectTopic({ topic_id: topic.id })
    fetchData()
  } catch { /* handled by interceptor */ }
}

async function handlePropose() {
  if (!proposeForm.value.title) return
  proposeLoading.value = true
  try {
    await proposeTopic(proposeForm.value)
    proposeForm.value = { title: '', description: '' }
    fetchData()
  } finally {
    proposeLoading.value = false
  }
}

onMounted(fetchData)
</script>
