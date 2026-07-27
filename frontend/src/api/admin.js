import request from './request'

export const getDashboard = () => request.get('/admin/dashboard')

export const getUsers = (params) => request.get('/admin/users', { params })
export const getUser = (id) => request.get(`/admin/users/${id}`)
export const createUser = (data) => request.post('/admin/users', data)
export const updateUser = (id, data) => request.put(`/admin/users/${id}`, data)
export const deleteUser = (id) => request.delete(`/admin/users/${id}`)

export const getProjects = (params) => request.get('/admin/projects', { params })
export const getProject = (id) => request.get(`/admin/projects/${id}`)
export const createProject = (data) => request.post('/admin/projects', data)
export const updateProject = (id, data) => request.put(`/admin/projects/${id}`, data)
export const deleteProject = (id) => request.delete(`/admin/projects/${id}`)

export const assignAdvisor = (data) => request.post('/admin/assignments/assign-advisor', data)
export const assignReviewer = (data) => request.post('/admin/assignments/assign-reviewer', data)
export const getAssignments = (params) => request.get('/admin/assignments', { params })

export const getStatusDefs = () => request.get('/admin/status-defs')
export const createStatusDef = (data) => request.post('/admin/status-defs', data)
export const updateStatusDef = (id, data) => request.put(`/admin/status-defs/${id}`, data)
export const deleteStatusDef = (id) => request.delete(`/admin/status-defs/${id}`)

export const getGraduationYears = () => request.get('/admin/graduation-years')
export const createGraduationYear = (data) => request.post('/admin/graduation-years', data)
export const updateGraduationYear = (id, data) => request.put(`/admin/graduation-years/${id}`, data)
export const deleteGraduationYear = (id) => request.delete(`/admin/graduation-years/${id}`)

export const setSubmissionLimit = (id, data) => request.put(`/admin/projects/${id}/submission-limit`, data)

export const getInteractions = (id) => request.get(`/admin/projects/${id}/interactions`)

export const exportEvaluationForms = (data) => request.post('/admin/export/evaluation-forms', data)
export const exportThesisMaterials = (data) => request.post('/admin/export/thesis-materials', data)

export const getLogs = (params) => request.get('/admin/logs', { params })

export const getTeacherList = () => request.get('/admin/teachers/list')
export const getStudentList = () => request.get('/admin/students/list')
