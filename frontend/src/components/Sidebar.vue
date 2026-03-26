<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { useI18n } from 'vue-i18n';
import {
  Monitor,
  OfficeBuilding,
  Grid,
  Tickets,
  User,
  DataAnalysis,
  Fold,
  Expand,
} from '@element-plus/icons-vue';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const isCollapsed = ref(false);

const userRole = computed(() => authStore.user?.role || '');

// Menu items configuration
const menuItems = [
  {
    label: 'admin.dashboard',
    path: '/admin/dashboard',
    icon: Monitor,
    roles: ['ADMIN', 'MANAGER', 'STAFF'],
  },
  {
    label: 'admin.hotels',
    path: '/admin/hotels',
    icon: OfficeBuilding,
    roles: ['ADMIN', 'MANAGER'],
  },
  {
    label: 'admin.rooms',
    path: '/admin/rooms',
    icon: Grid,
    roles: ['ADMIN', 'MANAGER', 'STAFF'],
  },
  {
    label: 'admin.bookings',
    path: '/admin/bookings',
    icon: Tickets,
    roles: ['ADMIN', 'MANAGER', 'STAFF'],
  },
  {
    label: 'admin.guests',
    path: '/admin/guests',
    icon: User,
    roles: ['ADMIN', 'MANAGER', 'STAFF'],
  },
  {
    label: 'admin.users',
    path: '/admin/users',
    icon: User,
    roles: ['ADMIN'],
  },
  {
    label: 'admin.reports',
    path: '/admin/reports',
    icon: DataAnalysis,
    roles: ['ADMIN', 'MANAGER'],
  },
];

// Filter menu items based on user role
const visibleMenuItems = computed(() => {
  return menuItems.filter((item) => item.roles.includes(userRole.value));
});

// Get active menu index
const activeMenu = computed(() => {
  const item = visibleMenuItems.value.find((m) => route.path.startsWith(m.path));
  return item?.path || '';
});

const onMenuSelect = (path) => {
  router.push(path);
};

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};
</script>

<template>
  <aside class="admin-sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <button class="collapse-btn" @click="toggleCollapse" title="Toggle Sidebar">
        <el-icon>
          <Fold v-if="!isCollapsed" />
          <Expand v-else />
        </el-icon>
      </button>
    </div>

    <nav class="sidebar-nav">
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        :collapse="isCollapsed"
        :unique-opened="false"
        background-color="transparent"
        text-color="inherit"
        active-text-color="var(--primary)"
      >
        <template v-for="item in visibleMenuItems" :key="item.path">
          <el-menu-item :index="item.path" @click="onMenuSelect(item.path)">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ t(item.label) }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </nav>
  </aside>
</template>

<style scoped>
.admin-sidebar {
  width: 250px;
  height: 100%;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 60px;
  z-index: 40;
}

.admin-sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
}

.collapse-btn {
  background: none;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 18px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.collapse-btn:hover {
  background-color: var(--primary-soft);
  color: var(--primary);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item) {
  color: var(--text-secondary);
  height: 40px;
  line-height: 40px;
  padding: 0 12px !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: var(--primary-soft) !important;
  color: var(--primary) !important;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: color-mix(in srgb, var(--primary) 8%, transparent) !important;
}

::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

@media (max-width: 768px) {
  .admin-sidebar {
    position: fixed;
    left: -250px;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
    z-index: 100;
  }

  .admin-sidebar.collapsed {
    left: -64px;
  }
}
</style>
