<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <el-icon :size="40" color="#409eff"><GraduationCap /></el-icon>
        <h2>注册账号</h2>
        <p>Graduation Design Management System</p>
      </div>

      <el-radio-group v-model="role" class="role-toggle">
        <el-radio-button value="student">注册为学生</el-radio-button>
        <el-radio-button value="teacher">注册为老师</el-radio-button>
      </el-radio-group>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        size="large"
        label-width="80px"
        @keyup.enter="handleRegister"
      >
        <template v-if="role === 'student'">
          <el-form-item label="学号" prop="student_id">
            <el-input v-model="form.student_id" placeholder="请输入学号" />
          </el-form-item>
          <el-form-item label="姓名" prop="name">
            <el-input v-model="form.name" placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="班级" prop="class_name">
            <el-input v-model="form.class_name" placeholder="请输入班级" />
          </el-form-item>
          <el-form-item label="专业" prop="major">
            <el-input v-model="form.major" placeholder="请输入专业" />
          </el-form-item>
          <el-form-item label="学院" prop="department">
            <el-input v-model="form.department" placeholder="请输入学院" />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号（选填）" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" placeholder="请输入邮箱（选填）" />
          </el-form-item>
        </template>

        <template v-if="role === 'teacher'">
          <el-form-item label="教师号" prop="teacher_id">
            <el-input v-model="form.teacher_id" placeholder="请输入教师号" />
          </el-form-item>
          <el-form-item label="姓名" prop="name">
            <el-input v-model="form.name" placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="学院" prop="department">
            <el-input v-model="form.department" placeholder="请输入学院" />
          </el-form-item>
          <el-form-item label="职业" prop="title">
            <el-input v-model="form.title" placeholder="请输入职业（如教授、副教授）" />
          </el-form-item>
          <el-form-item label="电话" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入电话（选填）" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" placeholder="请输入邮箱（选填）" />
          </el-form-item>
        </template>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" style="width:100%" @click="handleRegister">注 册</el-button>
        </el-form-item>
      </el-form>

      <div class="register-footer">
        <span>已有账号？</span>
        <el-link type="primary" @click="goLogin">返回登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register as registerApi, checkUsername } from '../../api/auth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const role = ref('student')

const form = reactive({
  student_id: '',
  teacher_id: '',
  name: '',
  class_name: '',
  major: '',
  department: '',
  title: '',
  phone: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const requiredText = (label) => ({ required: true, message: `请输入${label}`, trigger: 'blur' })

const rules = reactive({
  student_id: [
    requiredText('学号'),
    {
      validator: async (_rule, value, callback) => {
        if (!value) return callback()
        try {
          const res = await checkUsername(value, role.value)
          if (!res.available) {
            callback(new Error('该学号已被注册'))
          } else {
            callback()
          }
        } catch {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  teacher_id: [
    requiredText('教师号'),
    {
      validator: async (_rule, value, callback) => {
        if (!value) return callback()
        try {
          const res = await checkUsername(value, role.value)
          if (!res.available) {
            callback(new Error('该教师号已被注册'))
          } else {
            callback()
          }
        } catch {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  name: [requiredText('姓名')],
  class_name: [requiredText('班级')],
  major: [requiredText('专业')],
  department: [requiredText('学院')],
  title: [requiredText('职业')],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
})

watch(role, () => {
  if (formRef.value) {
    formRef.value.clearValidate()
  }
})

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const payload = {
      role: role.value,
      name: form.name,
      department: form.department,
      phone: form.phone || undefined,
      email: form.email || undefined,
      password: form.password,
    }
    if (role.value === 'student') {
      payload.student_id = form.student_id
      payload.class_name = form.class_name
      payload.major = form.major
    } else {
      payload.teacher_id = form.teacher_id
      payload.title = form.title
    }
    await registerApi(payload)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch {
    // error already handled by interceptor
  } finally {
    loading.value = false
  }
}

function goLogin() {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 0;
}
.register-card {
  width: 480px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.register-header { text-align: center; margin-bottom: 24px; }
.register-header h2 { margin: 12px 0 4px; font-size: 24px; }
.register-header p { color: #999; font-size: 13px; }
.role-toggle { display: flex; justify-content: center; margin-bottom: 24px; }
.register-footer { text-align: center; margin-top: 16px; }
</style>
