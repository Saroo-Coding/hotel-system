<script setup>
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { listHotels, deactivateHotel, activateHotel } from '@/api/dashboard.api';
import { Plus, Edit, CircleCheck, CircleClose } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useAuthStore } from '@/stores/auth.store';

const { t } = useI18n();
const authStore = useAuthStore();

const hotels = ref([]);
const loading = ref(false);
const currentRole = computed(() => authStore.user?.role || '');
const canManageHotels = computed(() => currentRole.value === 'ADMIN');

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
  if (!canManageHotels.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }
  ElMessage.info(t('common.add') + ' - Coming soon');
};

const handleEdit = (hotel) => {
  if (!canManageHotels.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }
  ElMessage.info(t('common.edit') + ' - Coming soon: ' + hotel.name);
};

const handleToggleStatus = (hotel) => {
  if (!canManageHotels.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }

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
        <el-button v-if="canManageHotels" type="primary" :icon="Plus" @click="handleAdd">
          {{ t('common.addNew') }}
        </el-button>
      </div>

      <el-table :data="hotels" stripe border class="hotels-table" v-loading="loading">
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
        <el-table-column v-if="canManageHotels" :label="t('common.actions')" width="170" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="large" class="action-btn" type="primary" :icon="Edit" @click="handleEdit(row)" text />
            <el-button 
              size="large"
              class="action-btn"
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
  font-size: 14px !important;
  font-weight: 700;
}

:deep(.el-table__body-wrapper tbody td) {
  padding: 14px 0;
}

:deep(.hotels-table) {
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

:deep(.hotels-table .el-table__header-wrapper th) {
  background: #f8fafc;
}

:deep(.action-btn .el-icon) {
  font-size: 20px;
}
</style>
