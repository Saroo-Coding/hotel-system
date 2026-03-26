<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { mockDashboardStats, mockBookings } from '@/mock-data';
import { BookingStatus } from '@/utils/constants';

const { t } = useI18n();

const stats = ref(mockDashboardStats);

const reportData = ref([
  {
    name: t('admin.reports.totalBookings'),
    value: mockBookings.length,
  },
  {
    name: t('admin.reports.pending'),
    value: mockBookings.filter((b) => b.status === BookingStatus.PENDING).length,
  },
  {
    name: t('admin.reports.confirmed'),
    value: mockBookings.filter((b) => b.status === BookingStatus.CONFIRMED).length,
  },
  {
    name: t('admin.reports.checkedIn'),
    value: mockBookings.filter((b) => b.status === BookingStatus.CHECKED_IN).length,
  },
  {
    name: t('admin.reports.checkedOut'),
    value: mockBookings.filter((b) => b.status === BookingStatus.CHECKED_OUT).length,
  },
  {
    name: t('admin.reports.cancelled'),
    value: mockBookings.filter((b) => b.status === BookingStatus.CANCELLED).length,
  },
]);
</script>

<template>
  <AdminLayout>
    <div class="reports-page">
      <div class="page-header">
        <h1>{{ t('admin.reports') }}</h1>
      </div>

      <!-- Summary Stats -->
      <el-row :gutter="20" class="stats-grid">
        <el-col v-for="(item, index) in reportData" :key="index" :xs="24" :sm="12" :lg="8">
          <el-card shadow="hover" class="stat-card">
            <p class="stat-name">{{ item.name }}</p>
            <p class="stat-value">{{ item.value }}</p>
          </el-card>
        </el-col>
      </el-row>

      <!-- Revenue Stats -->
      <el-row :gutter="20" class="charts-section">
        <el-col :xs="24" :lg="12">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>{{ t('admin.reports.weeklyRevenue') }}</span>
              </div>
            </template>
            <div class="chart-placeholder">
              <p class="chart-data">{{ stats.chartData.revenue.map(v => (v / 1000000).toFixed(1) + 'M').join(', ') }}</p>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>{{ t('admin.reports.weeklyBookings') }}</span>
              </div>
            </template>
            <div class="chart-placeholder">
              <p class="chart-data">{{ stats.chartData.bookings.join(', ') }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Detailed Table -->
      <el-card shadow="hover" class="details-card">
        <template #header>
          <div class="card-header">
            <span>{{ t('admin.reports.bookingsByDate') }}</span>
          </div>
        </template>
        <el-table :data="stats.chartData.dates.map((date, index) => ({
          date,
          bookings: stats.chartData.bookings[index],
          revenue: stats.chartData.revenue[index],
        }))" stripe>
          <el-table-column prop="date" :label="t('admin.reports.date')" />
          <el-table-column
            prop="bookings"
            :label="t('admin.reports.bookingsCount')"
            align="center"
          />
          <el-table-column
            prop="revenue"
            :label="t('admin.reports.revenueAmount')"
            align="right"
          >
            <template #default="{ row }">{{ (row.revenue / 1000000).toFixed(1) }}M</template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </AdminLayout>
</template>

<style scoped>
.reports-page {
  width: 100%;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.stats-grid {
  margin-bottom: 32px;
}

.stat-card {
  text-align: center;
  padding: 20px !important;
}

.stat-name {
  margin: 0 0 12px;
  color: var(--text-secondary);
  font-size: 14px;
}

.stat-value {
  margin: 0;
  font-size: 32px;
  font-weight: 600;
  color: var(--primary);
}

.charts-section {
  margin-bottom: 24px;
}

.chart-placeholder {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  border-radius: 4px;
}

.chart-data {
  margin: 0;
  color: var(--text-secondary);
  font-size: 12px;
  word-break: break-all;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.details-card {
  margin-top: 24px;
}
</style>
