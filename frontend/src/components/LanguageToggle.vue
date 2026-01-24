<script setup>
import { computed } from "vue";
import { useAppStore } from "@/stores/app.store";
import { ElButton } from "element-plus";

const appStore = useAppStore();

const currentLang = computed(() => appStore.lang);

function toggleLang() {
  appStore.toggleLang();
}
</script>

<template>
  <el-button
    :class="currentLang === 'vi' ? 'vi-el-btn' : 'en-el-btn'"
    @click="toggleLang"
  />
</template>

<style scoped>
.el-button:hover{
    background-color: var(--bg-primary);
    border-color: var(--bg-primary);
    color: var(--bg-primary);
    outline: none;
}

.vi-el-btn {
  background-image: url("@/assets/images/flag_vi.svg");
  background-size: cover;
  background-color: var(--bg-primary);
  border-color: var(--bg-primary);
}

.en-el-btn {
  background-image: url("@/assets/images/flag_en.svg");
  background-size: cover;
  background-color: var(--bg-primary);
  border-color: var(--bg-primary);
}
</style>
