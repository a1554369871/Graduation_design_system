import request from './request'

export const getMyStudents = (params) => request.get('/teacher/students', { params })
export const getPendingReviews = (params) => request.get('/teacher/pending-reviews', { params })
export const submitReview = (data) => request.post('/teacher/reviews', data)
export const withdrawReview = (id) => request.post(`/teacher/reviews/${id}/withdraw`)
export const getReviewHistory = (params) => request.get('/teacher/review-history', { params })
export const getProjectDetail = (id) => request.get(`/teacher/projects/${id}`)
export const downloadSubmission = (id) => request.get(`/teacher/submissions/${id}/download`, {
  responseType: 'blob',
})
export const advanceStage = (projectId) => request.post(`/teacher/projects/${projectId}/advance-stage`)
