<template>
  <div class="send-container">
    <el-card>
      <template #header>
        <span>发送通知</span>
      </template>

      <el-form label-width="100px" style="max-width:600px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="请输入通知标题" maxlength="256" show-word-limit />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="6"
            placeholder="请输入通知内容（选填）"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="过期时间">
          <el-date-picker
            v-model="form.expires_at"
            type="datetime"
            placeholder="设置通知自动过期时间（选填）"
            style="width:100%"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="sending" @click="handleSend">
            发送通知
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { sendAdminNotification } from '../../api/notification'

const sending = ref(false)
const form = reactive({
  title: '',
  content: '',
  expires_at: null,
})

function resetForm() {
  form.title = ''
  form.content = ''
  form.expires_at = null
}

async function handleSend() {
  if (!form.title) {
    ElMessage.warning('请输入标题')
    return
  }
  sending.value = true
  try {
    await sendAdminNotification({
      title: form.title,
      content: form.content,
      expires_at: form.expires_at || null,
    })
    ElMessage.success('发送成功')
    resetForm()
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
.send-container {
  max-width: 800px;
  margin: 0 auto;
}
</style>
