<script setup>
import { computed } from "vue";
import { useAppStore } from "@/stores/app.store";
import { ElButton } from "element-plus";

import flagVi from "@/assets/images/flag_vi.svg";
import flagEn from "@/assets/images/flag_en.svg";

const appStore = useAppStore();

const currentLang = computed(() => appStore.lang);

function toggleLang() {
  appStore.toggleLang();
}

const flagSrc = computed(() =>
  currentLang.value === "vi" ? flagVi : flagEn
);
</script>

<template>
  <el-button class="lang-btn" @click="toggleLang">
    <img :src="flagSrc" alt="language" />
  </el-button>
</template>

<style scoped>
.lang-btn {
  padding: 0;
  border: none;
  background: transparent;
  box-shadow: none;
}

.lang-btn:hover,
.lang-btn:focus {
  background: transparent;
}

.lang-btn img {
  width: 36px;
  height: 24px;
  object-fit: cover;
  border-radius: 4px;
  transition: transform 0.15s ease;
}

.lang-btn:hover img {
  transform: scale(1.08);
}
</style>
