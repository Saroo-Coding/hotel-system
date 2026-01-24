<script setup>
import { computed } from "vue";
import { useAppStore } from "@/stores/app.store";
import { ElSwitch } from "element-plus";
import { Moon, Sunny } from "@element-plus/icons-vue";

const appStore = useAppStore();

const isDark = computed(() => appStore.theme === "dark");

function toggleTheme() {
  appStore.toggleTheme();
}
</script>

<template>
  <el-switch
    :model-value="isDark"
    @change="toggleTheme"
    style="--el-switch-on-color: #a8abb2; --el-switch-off-color: #141414"
  >
    <template #active-action>
      <Sunny color="#141414" />
    </template>
    <template #inactive-action>
      <Moon color="#141414" />
    </template>
  </el-switch>
</template>
