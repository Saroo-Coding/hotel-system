<template>
  <div>
    <h1>Dashboard</h1>
    <pre>{{ auth.user }}</pre>
    <button @click="logout">Logout</button>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.store'

const auth = useAuthStore()
const logout = () => auth.logout()
</script>
