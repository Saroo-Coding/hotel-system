import { request } from './http'

export function meApi() {
  return request('/user/me')
}