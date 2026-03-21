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
  <div class="theme-toggle-wrapper">
    <el-switch
      class="theme-switch"
      :model-value="isDark"
      @change="toggleTheme"
      inline-prompt
    >
      <!-- DARK MODE -->
      <template #active-action>
        <Moon class="icon moon" />
      </template>

      <!-- LIGHT MODE -->
      <template #inactive-action>
        <Sunny class="icon sun" />
      </template>
    </el-switch>
  </div>
</template>

<style scoped>
.theme-toggle-wrapper {
  display: inline-flex;
  transition: transform 0.15s ease;
}

.theme-toggle-wrapper:hover {
  transform: scale(1.08);
}

.theme-switch {
  --el-switch-on-color: #ffffff;
  --el-switch-off-color: #1f2937;
}

.icon {
  width: 16px;
  height: 16px;
  color: #111827;
}
</style>
