<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { mockHotels } from '@/mock-data';
import { Plus, Edit, Delete } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const { t } = useI18n();

const hotels = ref(mockHotels);
const loading = ref(false);

const handleAdd = () => {
  ElMessage.info(t('common.add') + ' - Coming soon');
};

const handleEdit = (hotel) => {
  ElMessage.info(t('common.edit') + ' - Coming soon: ' + hotel.name);
};

const handleDelete = (hotel) => {
  ElMessageBox.confirm(
    t('admin.hotels.confirmDelete', { name: hotel.name }),
    t('admin.common.warning'),
    {
      confirmButtonText: t('common.ok'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    }
  )
    .then(() => {
      hotels.value = hotels.value.filter((h) => h.id !== hotel.id);
      ElMessage.success(t('admin.common.deleted'));
    })
    .catch(() => {});
};
</script>

<template>
  <AdminLayout>
    <div class="hotels-page">
      <div class="page-header">
        <h1>{{ t('admin.hotels') }}</h1>
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          {{ t('admin.common.addNew') }}
        </el-button>
      </div>

      <el-table :data="hotels" stripe v-loading="loading">
        <el-table-column prop="name" :label="t('admin.hotels.name')" />
        <el-table-column prop="city" :label="t('admin.hotels.city')" width="120" />
        <el-table-column prop="phone" :label="t('admin.hotels.phone')" width="140" />
        <el-table-column prop="rating" :label="t('admin.hotels.rating')" width="100" align="center" />
        <el-table-column
          prop="total_rooms"
          :label="t('admin.hotels.totalRooms')"
          width="120"
          align="center"
        />
        <el-table-column
          prop="available_rooms"
          :label="t('admin.hotels.availableRooms')"
          width="140"
          align="center"
        />
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
.hotels-page {
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
