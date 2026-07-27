import request from './request'

export function login(data) {
  return request.post('/auth/login', data)
}

export function getMe() {
  return request.get('/auth/me')
}

export function changePassword(data) {
  return request.put('/auth/change-password', data)
}

export function register(data) {
  return request.post('/auth/register', data)
}

export function checkUsername(username, role) {
  return request.get('/auth/check-username', { params: { username, role } })
}
