import { request } from './http'

export function loginApi(payload) {
  const formData = new URLSearchParams()
  formData.append('username', payload.username)
  formData.append('password', payload.password)

  return request('/auth/login', {
    method: 'POST',
    body: formData,
    headers: {}
  })
}