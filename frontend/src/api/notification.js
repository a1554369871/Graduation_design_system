import request from './request'

// Student
export const getStudentNotifications = (params) => request.get('/notifications/student', { params })
export const markNotificationRead = (id) => request.put(`/notifications/student/read/${id}`)

// Teacher
export const getAdminNotifications = () => request.get('/notifications/admin-list')
export const getTeacherStudentsProgress = (params) => request.get('/notifications/teacher/students-progress', { params })
export const sendTeacherNotification = (data) => request.post('/notifications/teacher/send', data)
export const getTeacherSentNotifications = () => request.get('/notifications/teacher/sent')
export const getTeacherStudentsList = (params) => request.get('/notifications/teacher/students-list', { params })

// Admin
export const sendAdminNotification = (data) => request.post('/notifications/admin/send', data)
export const getAllAdminNotifications = (params) => request.get('/notifications/admin/all', { params })
export const updateAdminNotification = (id, data) => request.put(`/notifications/admin/${id}`, data)
export const deleteAdminNotification = (id) => request.delete(`/notifications/admin/${id}`)
