<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { mockUsers } from '@/mock-data';
import { Plus, Edit, Lock, Unlock } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const { t } = useI18n();

const users = ref(mockUsers);
const loading = ref(false);

const handleAdd = () => {
  ElMessage.info(t('common.add') + ' - Coming soon');
};

const handleEdit = (user) => {
  ElMessage.info(t('common.edit') + ' - Coming soon: ' + user.full_name);
};

const handleLock = (user) => {
  users.value = users.value.map((u) =>
    u.id === user.id ? { ...u, is_active: false } : u
  );
  ElMessage.success(t('admin.users.locked'));
};

const handleUnlock = (user) => {
  users.value = users.value.map((u) =>
    u.id === user.id ? { ...u, is_active: true } : u
  );
  ElMessage.success(t('admin.users.unlocked'));
};

const handleDelete = (user) => {
  ElMessageBox.confirm(
    t('admin.users.confirmDelete', { name: user.full_name }),
    t('admin.common.warning'),
    {
      confirmButtonText: t('common.ok'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    }
  )
    .then(() => {
      users.value = users.value.filter((u) => u.id !== user.id);
      ElMessage.success(t('admin.common.deleted'));
    })
    .catch(() => {});
};
</script>

<template>
  <AdminLayout>
    <div class="users-page">
      <div class="page-header">
        <h1>{{ t('admin.users') }}</h1>
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          {{ t('admin.common.addNew') }}
        </el-button>
      </div>

      <el-table :data="users" stripe v-loading="loading">
        <el-table-column prop="email" :label="t('admin.users.email')" />
        <el-table-column prop="full_name" :label="t('admin.users.fullName')" />
        <el-table-column prop="role" :label="t('admin.users.role')" width="120" align="center">
          <template #default="{ row }">
            <el-tag effect="plain">{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" :label="t('admin.users.phone')" width="140" />
        <el-table-column prop="is_active" :label="t('admin.users.status')" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" effect="plain">
              {{ row.is_active ? t('admin.users.active') : t('admin.users.inactive') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('admin.common.actions')" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" :icon="Edit" @click="handleEdit(row)" text />
            <el-button
              v-if="row.is_active"
              size="small"
              type="warning"
              :icon="Lock"
              @click="handleLock(row)"
              text
            >
              {{ t('admin.users.lock') }}
            </el-button>
            <el-button
              v-else
              size="small"
              type="info"
              :icon="Unlock"
              @click="handleUnlock(row)"
              text
            >
              {{ t('admin.users.unlock') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </AdminLayout>
</template>

<style scoped>
.users-page {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}
</style>
