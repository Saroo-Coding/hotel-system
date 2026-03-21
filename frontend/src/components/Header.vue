<script setup>
import { useI18n } from "vue-i18n";
import ThemeToggle from "@/components/ThemeToggle.vue";
import LanguageToggle from "@/components/LanguageToggle.vue";

const { t } = useI18n();
</script>

<template>
  <el-header class="main-header">
    <div class="header-inner">
      <div class="logo">{{ t("dashboard.logo") }}</div>

      <div class="header-right">
        <el-menu
          mode="horizontal"
          default-active="home"
          class="main-menu"
          :ellipsis="false"
        >
          <el-menu-item index="home">{{ t("dashboard.home") }}</el-menu-item>
          <el-menu-item index="rooms">{{ t("dashboard.room") }}</el-menu-item>
        </el-menu>

        <div class="top-actions">
          <ThemeToggle />
          <LanguageToggle />
        </div>
      </div>
    </div>
  </el-header>
</template>

<style scoped>
.main-header {
  position: sticky;
  top: 0;
  z-index: 50;
  height: 60px;
  padding: 0;
  border-bottom: 1px solid var(--border-color);
  background: color-mix(in srgb, var(--bg-secondary) 88%, transparent);
  backdrop-filter: blur(12px);
  box-shadow: 0 10px 24px color-mix(in srgb, var(--primary) 8%, transparent);
}

.header-inner {
  max-width: 1120px;
  height: 100%;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.01em;
  color: var(--text-primary);
}

.main-menu {
  border-bottom: none;
  background: transparent;
}

.main-menu :deep(.el-menu-item) {
  color: var(--text-secondary);
}

.main-menu :deep(.el-menu-item.is-active) {
  color: var(--primary);
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 720px) {
  .header-inner {
    height: auto;
    min-height: 60px;
    padding-top: 8px;
    padding-bottom: 8px;
    flex-direction: column;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 640px) {
  .main-header {
    height: auto;
  }
}
</style>
