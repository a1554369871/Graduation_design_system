import request from './request'

export const getAvailableTopics = () => request.get('/topics/student/available-topics')
export const getMySelection = () => request.get('/topics/student/my-selection')
export const selectTopic = (data) => request.post('/topics/student/select', data)
export const proposeTopic = (data) => request.post('/topics/student/propose', data)

export const getMyTopics = () => request.get('/topics/teacher/topics')
export const createTopic = (data) => request.post('/topics/teacher/topics', data)
export const updateTopic = (id, data) => request.put(`/topics/teacher/topics/${id}`, data)
export const deleteTopic = (id) => request.delete(`/topics/teacher/topics/${id}`)

export const getPendingSelections = () => request.get('/topics/teacher/pending-selections')
export const getAllPendingSelections = () => request.get('/topics/teacher/all-pending-selections')
export const reviewSelection = (id, data) => request.post(`/topics/teacher/selections/${id}/review`, data)
export const getReviewedSelections = () => request.get('/topics/teacher/reviewed-selections')
