<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { mockGuests } from '@/mock-data';
import { Plus, Edit, Delete } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const { t } = useI18n();

const guests = ref(mockGuests);
const loading = ref(false);

const handleAdd = () => {
  ElMessage.info(t('common.add') + ' - Coming soon');
};

const handleEdit = (guest) => {
  ElMessage.info(t('common.edit') + ' - Coming soon: ' + guest.full_name);
};

const handleDelete = (guest) => {
  ElMessageBox.confirm(
    t('admin.guests.confirmDelete', { name: guest.full_name }),
    t('admin.common.warning'),
    {
      confirmButtonText: t('common.ok'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    }
  )
    .then(() => {
      guests.value = guests.value.filter((g) => g.id !== guest.id);
      ElMessage.success(t('admin.common.deleted'));
    })
    .catch(() => {});
};
</script>

<template>
  <AdminLayout>
    <div class="guests-page">
      <div class="page-header">
        <h1>{{ t('admin.guests') }}</h1>
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          {{ t('admin.common.addNew') }}
        </el-button>
      </div>

      <el-table :data="guests" stripe v-loading="loading">
        <el-table-column prop="full_name" :label="t('admin.guests.fullName')" />
        <el-table-column prop="email" :label="t('admin.guests.email')" />
        <el-table-column prop="phone" :label="t('admin.guests.phone')" width="140" />
        <el-table-column prop="date_of_birth" :label="t('admin.guests.dateOfBirth')" width="140" />
        <el-table-column prop="created_at" :label="t('admin.guests.createdAt')" width="160">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleDateString() }}
          </template>
        </el-table-column>
        <el-table-column :label="t('admin.common.actions')" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" :icon="Edit" @click="handleEdit(row)" text />
            <el-button size="small" type="danger" :icon="Delete" @click="handleDelete(row)" text />
          </template>
        </el-table-column>
      </el-table>
    </div>
  </AdminLayout>
</template>

<style scoped>
.guests-page {
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
