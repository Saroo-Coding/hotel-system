<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { mockRooms, mockHotels } from '@/mock-data';
import { STATUS_COLORS } from '@/utils/constants';
import { Plus, Edit, Delete } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const { t } = useI18n();

const rooms = ref(mockRooms);
const hotels = ref(mockHotels);
const loading = ref(false);
const filterHotelId = ref('');

const filteredRooms = ref(rooms);

const handleHotelFilter = (hotelId) => {
  if (hotelId === '') {
    filteredRooms.value = rooms.value;
  } else {
    filteredRooms.value = rooms.value.filter((r) => r.hotel_id === hotelId);
  }
};

const handleAdd = () => {
  ElMessage.info(t('common.add') + ' - Coming soon');
};

const handleEdit = (room) => {
  ElMessage.info(t('common.edit') + ' - Coming soon: Room ' + room.room_number);
};

const handleDelete = (room) => {
  ElMessageBox.confirm(
    t('admin.rooms.confirmDelete', { room: room.room_number }),
    t('admin.common.warning'),
    {
      confirmButtonText: t('common.ok'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    }
  )
    .then(() => {
      rooms.value = rooms.value.filter((r) => r.id !== room.id);
      filteredRooms.value = filteredRooms.value.filter((r) => r.id !== room.id);
      ElMessage.success(t('admin.common.deleted'));
    })
    .catch(() => {});
};
</script>

<template>
  <AdminLayout>
    <div class="rooms-page">
      <div class="page-header">
        <h1>{{ t('admin.rooms') }}</h1>
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          {{ t('admin.common.addNew') }}
        </el-button>
      </div>

      <el-card class="filter-card" shadow="hover">
        <el-select
          v-model="filterHotelId"
          :placeholder="t('admin.rooms.filterByHotel')"
          clearable
          @change="handleHotelFilter"
        >
          <el-option v-for="hotel in hotels" :key="hotel.id" :label="hotel.name" :value="hotel.id" />
        </el-select>
      </el-card>

      <el-table :data="filteredRooms" stripe v-loading="loading">
        <el-table-column prop="room_number" :label="t('admin.rooms.roomNumber')" width="120" />
        <el-table-column prop="floor" :label="t('admin.rooms.floor')" width="100" align="center" />
        <el-table-column
          prop="bed_type"
          :label="t('admin.rooms.bedType')"
          width="120"
          :filters="[
            { text: 'Single', value: 'SINGLE' },
            { text: 'Double', value: 'DOUBLE' },
          ]"
          :filter-method="(value, row) => row.bed_type === value"
        />
        <el-table-column prop="base_price" :label="t('admin.rooms.basePrice')" width="140" align="right">
          <template #default="{ row }">{{ row.base_price.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="status" :label="t('admin.rooms.status')" width="120" align="center">
          <template #default="{ row }">
            <el-tag :color="STATUS_COLORS[row.status]" effect="plain">
              {{ t('admin.room.' + row.status.toLowerCase()) }}
            </el-tag>
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

.filter-card {
  margin-bottom: 20px;
}
</style>
