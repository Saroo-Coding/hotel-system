<script setup>
import { useAuthStore } from '@/stores/auth.store';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { SwitchButton, User } from '@element-plus/icons-vue';
import ThemeToggle from '@/components/ThemeToggle.vue';
import LanguageToggle from '@/components/LanguageToggle.vue';
import Sidebar from '@/components/Sidebar.vue';

const { t } = useI18n();
const router = useRouter();
const authStore = useAuthStore();

const handleLogout = async () => {
  try {
    await authStore.logout();
    router.push('/login');
  } catch (err) {
    console.error('Logout error:', err);
  }
};

const handleProfile = () => {
  router.push('/profile');
};

const handleUserAction = (command) => {
  if (command === 'profile') {
    handleProfile();
  } else if (command === 'logout') {
    handleLogout();
  }
};
</script>

<template>
  <div class="admin-layout">
    <!-- Admin Header -->
    <header class="admin-header">
      <div class="header-inner">
        <h1 class="header-title">{{ t('dashboard.logo') }} - Admin</h1>

        <div class="header-actions">
          <ThemeToggle />
          <LanguageToggle />
          
          <el-dropdown v-if="authStore.user" @command="handleUserAction">
            <div class="user-avatar">
              <el-icon><User /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  <span>{{ authStore.user.full_name }}</span>
                  <span class="user-role">({{ authStore.user.role }})</span>
                </el-dropdown-item>
                <el-divider style="margin: 6px 0" />
                <el-dropdown-item command="profile">
                  {{ t('common.profile') }}
                </el-dropdown-item>
                <el-dropdown-item command="logout" class="logout-item">
                  <el-icon><SwitchButton /></el-icon>
                  {{ t('common.logout') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <div class="admin-container">
      <!-- Sidebar -->
      <Sidebar />

      <!-- Content -->
      <main class="admin-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-primary);
}

.admin-header {
  height: 60px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.header-inner {
  max-width: 100%;
  height: 100%;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary);
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.user-avatar:hover {
  background: var(--primary);
  color: white;
}

.user-role {
  margin-left: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.logout-item {
  color: var(--error);
}

.admin-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.admin-content {
  flex: 1;
  overflow-y: auto;
  margin-left: 250px;
  padding: 24px;
  transition: margin-left 0.3s ease;
}

/* When sidebar is collapsed, adjust margin */
:deep(.admin-sidebar.collapsed) ~ .admin-content {
  margin-left: 64px;
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

@media (max-width: 768px) {
  .admin-content {
    margin-left: 0;
    padding: 16px;
  }

  .header-title {
    font-size: 16px;
  }
}
</style>
