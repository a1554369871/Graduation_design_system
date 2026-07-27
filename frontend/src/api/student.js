import request from './request'

export const getMyProject = () => request.get('/student/my-project')
export const getPaperStatus = () => request.get('/student/paper-status')
export const getCurrentStage = () => request.get('/student/current-stage')
export const submitPaper = (formData) => request.post('/student/submit-paper', formData)
export const getSubmissions = () => request.get('/student/submissions')
export const downloadSubmission = (id) => request.get(`/student/submissions/${id}/download`, {
  responseType: 'blob',
})
