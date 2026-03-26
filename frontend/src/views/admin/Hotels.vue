<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { listHotels, deactivateHotel, activateHotel } from '@/api/dashboard.api';
import { Plus, Edit, CircleCheck, CircleClose } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const { t } = useI18n();

const hotels = ref([]);
const loading = ref(false);

const fetchHotels = async () => {
  loading.value = true;
  try {
    const response = await listHotels();
    hotels.value = response.data || [];
  } catch (error) {
    ElMessage.error(t('common.internal_server_error'));
    console.error('Failed to fetch hotels:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchHotels();
});

const handleAdd = () => {
  ElMessage.info(t('common.add') + ' - Coming soon');
};

const handleEdit = (hotel) => {
  ElMessage.info(t('common.edit') + ' - Coming soon: ' + hotel.name);
};

const handleToggleStatus = (hotel) => {
  const isActive = hotel.status === 'ACTIVE';
  const message = isActive 
    ? `Deactivate ${hotel.name}?`
    : `Activate ${hotel.name}?`;
  const action = isActive ? 'deactivate' : 'activate';
  const type = isActive ? 'warning' : 'success';
  
  ElMessageBox.confirm(
    message,
    t('common.warning'),
    {
      confirmButtonText: t('common.ok'),
      cancelButtonText: t('common.cancel'),
      type: type,
    }
  )
    .then(async () => {
      try {
        loading.value = true;
        if (isActive) {
          await deactivateHotel(hotel.id);
        } else {
          await activateHotel(hotel.id);
        }
        hotel.status = isActive ? 'INACTIVE' : 'ACTIVE';
        ElMessage.success(`Hotel ${action}d successfully`);
      } catch (error) {
        ElMessage.error(t('common.internal_server_error'));
        console.error(`Failed to ${action} hotel:`, error);
      } finally {
        loading.value = false;
      }
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
          {{ t('common.addNew') }}
        </el-button>
      </div>

      <el-table :data="hotels" stripe v-loading="loading" style="width: 100%; font-size: 15px;">
        <el-table-column prop="name" :label="t('hotels.name')" min-width="200" />
        <el-table-column prop="phone" :label="t('hotels.phone')" width="140" />
        <el-table-column
          prop="total_rooms"
          :label="t('hotels.totalRooms')"
          width="120"
          align="center"
        />
        <el-table-column
          prop="available_rooms"
          :label="t('hotels.availableRooms')"
          width="140"
          align="center"
        />
        <el-table-column prop="status" :label="t('hotels.status')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="large" type="primary" :icon="Edit" @click="handleEdit(row)" text />
            <el-button 
              :size="'large'"
              :type="row.status === 'ACTIVE' ? 'danger' : 'success'"
              :icon="row.status === 'ACTIVE' ? CircleClose : CircleCheck"
              @click="handleToggleStatus(row)" 
              text 
            />
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
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
}

:deep(.el-table__header-wrapper th) {
  font-size: 16px !important;
  font-weight: 600;
}

:deep(.el-table__body-wrapper tbody td) {
  font-size: 15px;
  padding: 14px 0;
}
</style>
