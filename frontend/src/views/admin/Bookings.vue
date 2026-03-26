<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { mockBookings, mockRooms, mockGuests, mockHotels } from '@/mock-data';
import { STATUS_COLORS } from '@/utils/constants';
import { Check, Close } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

const { t } = useI18n();

const bookings = ref(mockBookings);
const loading = ref(false);
const filterStatus = ref('');

const getHotelName = (hotelId) =>  mockHotels.find((h) => h.id === hotelId)?.name || '-';
const getRoomNumber = (roomId) => mockRooms.find((r) => r.id === roomId)?.room_number || '-';
const getGuestName = (guestId) => mockGuests.find((g) => g.id === guestId)?.full_name || '-';

const filteredBookings = ref(bookings);

const handleStatusFilter = (status) => {
  if (status === '') {
    filteredBookings.value = bookings.value;
  } else {
    filteredBookings.value = bookings.value.filter((b) => b.status === status);
  }
};

const handleConfirm = (booking) => {
  ElMessage.success(t('admin.bookings.confirmed'));
};

const handleCancel = (booking) => {
  ElMessage.success(t('admin.bookings.cancelled'));
};
</script>

<template>
  <AdminLayout>
    <div class="bookings-page">
      <div class="page-header">
        <h1>{{ t('admin.bookings') }}</h1>
        <el-select
          v-model="filterStatus"
          :placeholder="t('admin.bookings.filterByStatus')"
          clearable
          @change="handleStatusFilter"
          style="width: 200px"
        >
          <el-option value="PENDING" :label="t('admin.booking.pending')" />
          <el-option value="CONFIRMED" :label="t('admin.booking.confirmed')" />
          <el-option value="CHECKED_IN" :label="t('admin.booking.checkedIn')" />
          <el-option value="CHECKED_OUT" :label="t('admin.booking.checkedOut')" />
          <el-option value="CANCELLED" :label="t('admin.booking.cancelled')" />
        </el-select>
      </div>

      <el-table :data="filteredBookings" stripe v-loading="loading">
        <el-table-column prop="booking_code" :label="t('admin.bookings.code')" width="120" />
        <el-table-column :label="t('admin.bookings.hotel')" width="180">
          <template #default="{ row }">{{ getHotelName(row.hotel_id) }}</template>
        </el-table-column>
        <el-table-column :label="t('admin.bookings.room')" width="100" align="center">
          <template #default="{ row }">{{ getRoomNumber(row.room_id) }}</template>
        </el-table-column>
        <el-table-column :label="t('admin.bookings.guest')" width="140">
          <template #default="{ row }">{{ getGuestName(row.guest_id) }}</template>
        </el-table-column>
        <el-table-column prop="checkin_date" :label="t('admin.bookings.checkInDate')" width="140" />
        <el-table-column prop="checkout_date" :label="t('admin.bookings.checkOutDate')" width="140" />
        <el-table-column prop="status" :label="t('admin.bookings.status')" width="120" align="center">
          <template #default="{ row }">
            <el-tag :color="STATUS_COLORS[row.status]" effect="plain">
              {{ t('admin.booking.' + row.status.toLowerCase()) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_price" :label="t('admin.bookings.totalPrice')" width="140" align="right">
          <template #default="{ row }">{{ row.total_price.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column :label="t('admin.common.actions')" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'PENDING'"
              size="small"
              type="success"
              :icon="Check"
              @click="handleConfirm(row)"
              text
            >
              {{ t('admin.bookings.confirm') }}
            </el-button>
            <el-button
              v-if="row.status !== 'CANCELLED' && row.status !== 'CHECKED_OUT'"
              size="small"
              type="danger"
              :icon="Close"
              @click="handleCancel(row)"
              text
            >
              {{ t('admin.bookings.cancelBooking') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </AdminLayout>
</template>

<style scoped>
.bookings-page {
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
