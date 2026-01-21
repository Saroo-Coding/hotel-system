import { defineStore } from 'pinia'
import { loginApi } from '@/api/auth.api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null
  }),

  actions: {
    async login(username, password) {
      const res = await loginApi({ username, password })

      this.token = res.access_token
      localStorage.setItem('token', res.access_token)
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
    }
  }
})
