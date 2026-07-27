<template>
  <el-container style="height: 100vh">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo" @click="router.push('/dashboard')">
        <el-icon :size="24"><GraduationCap /></el-icon>
        <span v-show="!isCollapse">毕设管理系统</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        background-color="#001529"
        text-color="#ffffff99"
        active-text-color="#fff"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-sub-menu v-if="isAdmin" index="admin">
          <template #title><el-icon><Setting /></el-icon><span>系统管理</span></template>
          <el-menu-item index="/admin/users">用户管理</el-menu-item>
          <el-menu-item index="/admin/projects">项目管理</el-menu-item>
          <el-menu-item index="/admin/assignments">教师分配</el-menu-item>
          <el-menu-item index="/admin/status-defs">状态管理</el-menu-item>
          <el-menu-item index="/admin/graduation-years">年份管理</el-menu-item>
          <el-menu-item index="/admin/logs">操作日志</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="isStudent" index="student-notice">
          <template #title><el-icon><Bell /></el-icon><span>通告管理</span></template>
          <el-menu-item index="/student/notifications">通知</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="isTeacher" index="teacher-notice">
          <template #title><el-icon><Bell /></el-icon><span>通告管理</span></template>
          <el-menu-item index="/teacher/notifications">通知</el-menu-item>
          <el-menu-item index="/teacher/student-progress">指导管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="isAdmin" index="admin-notice">
          <template #title><el-icon><Bell /></el-icon><span>通告管理</span></template>
          <el-menu-item index="/admin/send-notification">发送通知</el-menu-item>
          <el-menu-item index="/admin/manage-notifications">管理通知</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="isTeacher" index="teacher">
          <template #title><el-icon><UserFilled /></el-icon><span>教师工作台</span></template>
          <el-menu-item index="/teacher/students">我的学生</el-menu-item>
          <el-menu-item index="/teacher/pending-reviews">待评审</el-menu-item>
          <el-menu-item index="/teacher/review-history">评审历史</el-menu-item>
          <el-menu-item index="/teacher/topics">选题管理</el-menu-item>
          <el-menu-item index="/teacher/topic-reviews">选题审核</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="isStudent" index="student">
          <template #title><el-icon><Document /></el-icon><span>毕设管理</span></template>
          <el-menu-item index="/student/topic-selection">选题管理</el-menu-item>
          <el-sub-menu index="student-paper">
            <template #title><span>论文管理</span></template>
            <el-menu-item index="/student/paper-draft">初稿</el-menu-item>
            <el-menu-item index="/student/paper-round1">一轮</el-menu-item>
            <el-menu-item index="/student/paper-round2">二轮</el-menu-item>
            <el-menu-item index="/student/paper-round3">三轮</el-menu-item>
            <el-menu-item index="/student/paper-final-check">查重定稿</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/student/final-submission">最终稿</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" /><Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta.title">{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <span class="user-info">{{ userName }} · {{ roleText }}</span>
          <el-button text @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const isCollapse = ref(false)
const userName = computed(() => auth.userName)
const isAdmin = computed(() => auth.isAdmin)
const isTeacher = computed(() => auth.isTeacher)
const isStudent = computed(() => auth.isStudent)
const roleText = computed(() => {
  if (isAdmin.value) return '管理员'
  if (isTeacher.value) return '教师'
  if (isStudent.value) return '学生'
  return ''
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.aside {
  background: #001529;
  overflow-y: auto;
  transition: width 0.3s;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  gap: 8px;
}
.el-menu { border-right: none; }
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #eee;
  padding: 0 20px;
}
.header-left { display: flex; align-items: center; gap: 16px; }
.collapse-btn { font-size: 20px; cursor: pointer; }
.header-right { display: flex; align-items: center; gap: 12px; }
.user-info { font-size: 14px; color: #666; }
.main {
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
}
</style>
