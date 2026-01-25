<script setup>
import { useAuthStore } from "@/stores/auth.store";

const authStore = useAuthStore();
</script>

<template>
  <div style="padding: 24px">
    <h2>USER INFO (RAW)</h2>

    <pre v-if="authStore.user">
{{ JSON.stringify(authStore.user, null, 2) }}
<p>Initialized: {{ authStore.initialized }}</p>
<p>Token: {{ authStore.token }}</p>

    </pre>

    <p v-else>Loading...</p>
  </div>
</template>
