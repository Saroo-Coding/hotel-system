<template>
  <div style="max-width: 300px; margin: 100px auto;">
    <h2>Login</h2>

    <input v-model="username" placeholder="Username" />
    <br /><br />

    <input v-model="password" type="password" placeholder="Password" />
    <br /><br />

    <button @click="submit">Login</button>

    <p v-if="error" style="color:red">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const username = ref('')
const password = ref('')
const error = ref('')
const authStore = useAuthStore()
const router = useRouter()

const submit = async () => {
  error.value = ''
  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.message || 'Login failed'
  }
}
</script>
