import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

const routes = [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/login/Login.vue'),
      meta: { layout: 'blank' },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/login/Register.vue'),
      meta: { layout: 'blank' },
    },
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '首页' } },
      // Admin
      { path: 'admin/users', name: 'AdminUsers', component: () => import('../views/admin/UserManagement.vue'), meta: { title: '用户管理', role: 'admin' } },
      { path: 'admin/projects', name: 'AdminProjects', component: () => import('../views/admin/ProjectManagement.vue'), meta: { title: '项目管理', role: 'admin' } },
      { path: 'admin/assignments', name: 'AdminAssignments', component: () => import('../views/admin/AssignmentManagement.vue'), meta: { title: '教师分配', role: 'admin' } },
      { path: 'admin/status-defs', name: 'AdminStatusDefs', component: () => import('../views/admin/StatusManagement.vue'), meta: { title: '状态管理', role: 'admin' } },
      { path: 'admin/graduation-years', name: 'AdminYears', component: () => import('../views/admin/YearManagement.vue'), meta: { title: '年份管理', role: 'admin' } },
      { path: 'admin/logs', name: 'AdminLogs', component: () => import('../views/admin/Logs.vue'), meta: { title: '操作日志', role: 'admin' } },
      // Teacher
      { path: 'teacher/students', name: 'TeacherStudents', component: () => import('../views/teacher/MyStudents.vue'), meta: { title: '我的学生', role: 'teacher' } },
      { path: 'teacher/pending-reviews', name: 'TeacherPendingReviews', component: () => import('../views/teacher/PendingReviews.vue'), meta: { title: '待评审', role: 'teacher' } },
      { path: 'teacher/review-history', name: 'TeacherReviewHistory', component: () => import('../views/teacher/ReviewHistory.vue'), meta: { title: '评审历史', role: 'teacher' } },
      { path: 'teacher/notifications', name: 'TeacherNotifications', component: () => import('../views/teacher/AdminNotifications.vue'), meta: { title: '通知', role: 'teacher' } },
      { path: 'teacher/student-progress', name: 'TeacherStudentProgress', component: () => import('../views/teacher/StudentProgress.vue'), meta: { title: '指导管理', role: 'teacher' } },
      { path: 'teacher/topics', name: 'TeacherTopics', component: () => import('../views/teacher/TopicsManagement.vue'), meta: { title: '选题管理', role: 'teacher' } },
      { path: 'teacher/topic-reviews', name: 'TeacherTopicReviews', component: () => import('../views/teacher/TopicReview.vue'), meta: { title: '选题审核', role: 'teacher' } },
      // Student - 选题管理
      { path: 'student/topic-selection', name: 'StudentTopicSelection', component: () => import('../views/student/TopicSelection.vue'), meta: { title: '选题管理', role: 'student' } },
      // Student - 论文管理
      { path: 'student/paper-draft', name: 'StudentPaperDraft', component: () => import('../views/student/PaperDraft.vue'), meta: { title: '初稿', role: 'student' } },
      { path: 'student/paper-round1', name: 'StudentPaperRound1', component: () => import('../views/student/PaperRound1.vue'), meta: { title: '一轮', role: 'student' } },
      { path: 'student/paper-round2', name: 'StudentPaperRound2', component: () => import('../views/student/PaperRound2.vue'), meta: { title: '二轮', role: 'student' } },
      { path: 'student/paper-round3', name: 'StudentPaperRound3', component: () => import('../views/student/PaperRound3.vue'), meta: { title: '三轮', role: 'student' } },
      { path: 'student/paper-final-check', name: 'StudentPaperFinalCheck', component: () => import('../views/student/PaperFinalCheck.vue'), meta: { title: '查重定稿', role: 'student' } },
      { path: 'student/final-submission', name: 'StudentFinalSubmission', component: () => import('../views/student/FinalSubmission.vue'), meta: { title: '最终稿', role: 'student' } },
      // Student - 通知
      { path: 'student/notifications', name: 'StudentNotifications', component: () => import('../views/student/Notifications.vue'), meta: { title: '通告管理', role: 'student' } },
      // Admin
      { path: 'admin/send-notification', name: 'AdminSendNotification', component: () => import('../views/admin/SendNotification.vue'), meta: { title: '发送通知', role: 'admin' } },
      { path: 'admin/manage-notifications', name: 'AdminManageNotifications', component: () => import('../views/admin/ManageNotifications.vue'), meta: { title: '管理通知', role: 'admin' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  let user = null
  try {
    user = JSON.parse(localStorage.getItem('user'))
  } catch { /* ignore */ }

  if (to.path !== '/login' && to.path !== '/register' && !token) {
    return next('/login')
  }

  if ((to.path === '/login' || to.path === '/register') && token) {
    return next('/dashboard')
  }

  const role = user?.role
  if (to.meta.role && to.meta.role !== role) {
    return next('/dashboard')
  }

  next()
})

export default router
