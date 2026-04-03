<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { createAdminRoom, listAdminRooms, listHotels, setRoomAvailable, setRoomMaintenance, updateAdminRoom } from '@/api/dashboard.api';
import { STATUS_COLORS } from '@/utils/constants';
import { Plus, Edit, Refresh, CircleCheck, CircleClose, Lock } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useAuthStore } from '@/stores/auth.store';

const { t } = useI18n();
const authStore = useAuthStore();

const rooms = ref([]);
const hotels = ref([]);
const loading = ref(false);
const submitting = ref(false);

const dialogVisible = ref(false);
const dialogMode = ref('create');
const formRef = ref(null);

const defaultForm = () => ({
  id: null,
  hotel_id: '',
  room_number: '',
  floor: 1,
  bed_type: 'SINGLE',
  base_price: 100000,
  status: 'AVAILABLE',
  description: '',
  image: '',
});

const roomForm = reactive(defaultForm());

const currentRole = computed(() => authStore.user?.role || '');
const canCreateRoom = computed(() => currentRole.value === 'ADMIN');
const canUpdateRoom = computed(() => currentRole.value === 'ADMIN' || currentRole.value === 'STAFF');
const canToggleRoomStatus = computed(() => currentRole.value === 'ADMIN' || currentRole.value === 'STAFF');
const hasRoomActions = computed(() => canUpdateRoom.value || canToggleRoomStatus.value);

const formRules = computed(() => ({
  hotel_id: [{ required: true, message: t('rooms.validation.hotelRequired'), trigger: 'change' }],
  room_number: [{ required: true, message: t('rooms.validation.roomNumberRequired'), trigger: 'blur' }],
  floor: [{ required: true, message: t('rooms.validation.floorRequired'), trigger: 'change' }],
  bed_type: [{ required: true, message: t('rooms.validation.bedTypeRequired'), trigger: 'change' }],
  base_price: [{ required: true, message: t('rooms.validation.basePriceRequired'), trigger: 'change' }],
  status: [{ required: true, message: t('rooms.validation.statusRequired'), trigger: 'change' }],
}));

const hotelNameMap = computed(() => {
  const map = {};
  for (const hotel of hotels.value) {
    map[hotel.id] = hotel.name;
  }
  return map;
});

const getErrorMessage = (error, fallbackKey = 'common.internal_server_error') => {
  if (typeof error?.detail === 'string') {
    return t(error.detail);
  }

  if (Array.isArray(error?.detail) && error.detail.length > 0) {
    const firstMsg = String(error.detail[0]?.msg || '');
    const matchedI18nKey = firstMsg.match(/rooms\.validation\.[a-zA-Z0-9_]+/)?.[0];
    if (matchedI18nKey) {
      return t(matchedI18nKey);
    }
    return firstMsg || t(fallbackKey);
  }

  if (error?.detail && typeof error.detail === 'object') {
    const firstFieldError = Object.values(error.detail)[0];
    if (typeof firstFieldError === 'string') {
      return t(firstFieldError);
    }
  }

  return t(fallbackKey);
};

const resetForm = () => {
  Object.assign(roomForm, defaultForm());
};

const fetchInitialData = async () => {
  loading.value = true;
  try {
    const [roomsResponse, hotelsResponse] = await Promise.all([listAdminRooms(), listHotels()]);
    rooms.value = roomsResponse.data || [];
    hotels.value = hotelsResponse.data || [];
  } catch (error) {
    ElMessage.error(getErrorMessage(error));
  } finally {
    loading.value = false;
  }
};

const openCreateDialog = () => {
  if (!canCreateRoom.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }
  dialogMode.value = 'create';
  resetForm();
  dialogVisible.value = true;
};

const openEditDialog = (room) => {
  if (!canUpdateRoom.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }
  dialogMode.value = 'edit';
  Object.assign(roomForm, {
    hotel_id: room.hotel_id,
    room_number: room.room_number,
    floor: room.floor,
    bed_type: room.bed_type,
    base_price: room.base_price,
    status: room.status,
    description: room.description || '',
    image: room.image || '',
    id: room.id,
  });
  dialogVisible.value = true;
};

const submitRoomForm = async () => {
  if (dialogMode.value === 'create' && !canCreateRoom.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }
  if (dialogMode.value === 'edit' && !canUpdateRoom.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }

  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitting.value = true;
  try {
    const payload = {
      hotel_id: roomForm.hotel_id,
      room_number: roomForm.room_number?.trim(),
      floor: roomForm.floor,
      bed_type: roomForm.bed_type,
      base_price: roomForm.base_price,
      status: roomForm.status,
      description: roomForm.description?.trim() || null,
      image: roomForm.image?.trim() || null,
    };

    if (dialogMode.value === 'create') {
      await createAdminRoom(payload);
      ElMessage.success(t('rooms.messages.created'));
    } else {
      await updateAdminRoom(roomForm.id, payload);
      ElMessage.success(t('rooms.messages.updated'));
    }

    dialogVisible.value = false;
    resetForm();
    await fetchInitialData();
  } catch (error) {
    ElMessage.error(getErrorMessage(error));
  } finally {
    submitting.value = false;
  }
};

const handleToggleStatus = async (room) => {
  if (!canToggleRoomStatus.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }

  try {
    if (room.status === 'BOOKED') {
      ElMessage.info(t('rooms.messages.bookedStatusLocked'));
      return;
    }

    const isMaintenance = room.status === 'MAINTENANCE';
    const confirmMessage = isMaintenance
      ? t('rooms.confirmAvailable', { room: room.room_number })
      : t('rooms.confirmMaintenance', { room: room.room_number });

    await ElMessageBox.confirm(
      confirmMessage,
      t('common.warning'),
      {
        confirmButtonText: t('common.ok'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
      }
    );

    loading.value = true;
    if (isMaintenance) {
      await setRoomAvailable(room.id);
      ElMessage.success(t('rooms.messages.markedAvailable'));
    } else {
      await setRoomMaintenance(room.id);
      ElMessage.success(t('rooms.messages.markedMaintenance'));
    }
    await fetchInitialData();
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(getErrorMessage(error));
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchInitialData();
});
</script>

<template>
  <AdminLayout>
    <div class="rooms-page">
      <div class="page-header">
        <h1>{{ t('admin.rooms') }}</h1>
        <div class="actions">
          <el-button :icon="Refresh" @click="fetchInitialData">{{ t('rooms.refresh') }}</el-button>
          <el-button v-if="canCreateRoom" type="primary" :icon="Plus" @click="openCreateDialog">
            {{ t('common.addNew') }}
          </el-button>
        </div>
      </div>

      <el-table :data="rooms" stripe border class="rooms-table" v-loading="loading">
        <el-table-column prop="room_number" :label="t('rooms.roomNumber')" min-width="120" />
        <el-table-column :label="t('rooms.hotel')" min-width="220">
          <template #default="{ row }">{{ hotelNameMap[row.hotel_id] || row.hotel_id }}</template>
        </el-table-column>
        <el-table-column prop="floor" :label="t('rooms.floor')" width="100" align="center" />
        <el-table-column prop="bed_type" :label="t('rooms.bedType')" width="140">
          <template #default="{ row }">{{ t(`room.bedTypeOptions.${row.bed_type}`) }}</template>
        </el-table-column>
        <el-table-column prop="base_price" :label="t('rooms.basePrice')" width="150" align="right">
          <template #default="{ row }">{{ Number(row.base_price).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="status" :label="t('rooms.status')" width="140" align="center">
          <template #default="{ row }">
            <el-tag :color="STATUS_COLORS[row.status]" effect="plain">
              {{ t(`rooms.${row.status.toLowerCase()}`) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="hasRoomActions" :label="t('common.actions')" width="170" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="canUpdateRoom"
              size="large"
              class="action-btn"
              type="primary"
              :icon="Edit"
              @click="openEditDialog(row)"
              text
            />
            <el-button
              v-if="canToggleRoomStatus && row.status === 'AVAILABLE'"
              size="large"
              class="action-btn"
              type="warning"
              :icon="CircleClose"
              @click="handleToggleStatus(row)"
              text
            />
            <el-button
              v-else-if="canToggleRoomStatus && row.status === 'MAINTENANCE'"
              size="large"
              class="action-btn"
              type="success"
              :icon="CircleCheck"
              @click="handleToggleStatus(row)"
              text
            />
            <el-button
              v-else-if="canToggleRoomStatus"
              size="large"
              class="action-btn"
              type="info"
              :icon="Lock"
              disabled
              text
            />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? t('rooms.dialog.createTitle') : t('rooms.dialog.editTitle')"
      width="620px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="roomForm" :rules="formRules" label-position="top">
        <el-form-item :label="t('rooms.hotel')" prop="hotel_id">
          <el-select v-model="roomForm.hotel_id" filterable>
            <el-option v-for="hotel in hotels" :key="hotel.id" :label="hotel.name" :value="hotel.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('rooms.roomNumber')" prop="room_number">
          <el-input v-model="roomForm.room_number" />
        </el-form-item>
        <el-form-item :label="t('rooms.floor')" prop="floor">
          <el-input-number v-model="roomForm.floor" :min="1" />
        </el-form-item>
        <el-form-item :label="t('rooms.bedType')" prop="bed_type">
          <el-select v-model="roomForm.bed_type">
            <el-option :label="t('room.bedTypeOptions.SINGLE')" value="SINGLE" />
            <el-option :label="t('room.bedTypeOptions.DOUBLE')" value="DOUBLE" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('rooms.basePrice')" prop="base_price">
          <el-input-number v-model="roomForm.base_price" :min="1000" :step="10000" />
        </el-form-item>
        <el-form-item :label="t('rooms.status')" prop="status">
          <el-select v-model="roomForm.status">
            <el-option :label="t('rooms.available')" value="AVAILABLE" />
            <el-option :label="t('rooms.booked')" value="BOOKED" />
            <el-option :label="t('rooms.maintenance')" value="MAINTENANCE" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('rooms.description')">
          <el-input v-model="roomForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item :label="t('rooms.image')">
          <el-input v-model="roomForm.image" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="submitRoomForm">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<style scoped>
.rooms-page {
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

.actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

:deep(.rooms-table) {
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

:deep(.rooms-table .el-table__header-wrapper th) {
  background: #f8fafc;
  font-size: 14px;
  font-weight: 700;
}

:deep(.rooms-table .el-table__body-wrapper td) {
  padding: 14px 0;
}

:deep(.action-btn .el-icon) {
  font-size: 20px;
}
</style>
