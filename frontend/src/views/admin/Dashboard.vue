<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { mockDashboardStats } from '@/mock-data';
import { DataAnalysis, User, Grid, CreditCard } from '@element-plus/icons-vue';

const { t } = useI18n();

const stats = ref(mockDashboardStats);

const summaryCards = computed(() => [
  {
    title: 'adminDashboard.totalBookings',
    value: stats.value.totalBookings,
    icon: CreditCard,
    color: '#409EFF',
  },
  {
    title: 'adminDashboard.totalRevenue',
    value: `${(stats.value.totalRevenue / 1000000).toFixed(1)}M`,
    icon: DataAnalysis,
    color: '#67C26A',
  },
  {
    title: 'adminDashboard.occupiedRooms',
    value: stats.value.occupiedRooms,
    icon: Grid,
    color: '#E6A23C',
  },
  {
    title: 'adminDashboard.availableRooms',
    value: stats.value.availableRooms,
    icon: User,
    color: '#F56C6C',
  },
]);

const todayStats = computed(() => [
  {
    label: 'adminDashboard.todayCheckIns',
    value: stats.value.todayCheckIns,
  },
  {
    label: 'adminDashboard.todayCheckOuts',
    value: stats.value.todayCheckOuts,
  },
  {
    label: 'adminDashboard.pendingBookings',
    value: stats.value.pendingBookings,
  },
]);
</script>

<template>
  <AdminLayout>
    <div class="dashboard-page">
      <div class="page-header">
        <h1>{{ t('adminDashboard.title') }}</h1>
        <p>{{ t('adminDashboard.subtitle') }}</p>
      </div>

      <!-- Summary Cards -->
      <el-row :gutter="20" class="summary-cards">
        <el-col v-for="(card, index) in summaryCards" :key="index" :xs="24" :sm="12" :lg="6">
          <div class="summary-card" :style="{ borderTopColor: card.color }">
            <div class="card-icon" :style="{ backgroundColor: `${card.color}20` }">
              <el-icon :style="{ color: card.color }">
                <component :is="card.icon" />
              </el-icon>
            </div>
            <div class="card-content">
              <p class="card-title">{{ t(card.title) }}</p>
              <p class="card-value">{{ card.value }}</p>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Today Stats -->
      <el-row :gutter="20" class="today-stats">
        <el-col v-for="(stat, index) in todayStats" :key="index" :xs="24" :sm="12" :lg="8">
          <div class="stat-item">
            <span class="stat-label">{{ t(stat.label) }}</span>
            <span class="stat-value">{{ stat.value }}</span>
          </div>
        </el-col>
      </el-row>

      <!-- Charts Section -->
      <el-row :gutter="20" class="charts-section">
        <el-col :xs="24" :lg="12" class="chart-container">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>{{ t('adminDashboard.bookingTrend') }}</span>
              </div>
            </template>
            <div class="chart-placeholder">
              <p>{{ t('adminDashboard.chartLoading') }}</p>
              <p class="chart-data">{{ stats.chartData.bookings.join(', ') }}</p>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="12" class="chart-container">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>{{ t('adminDashboard.revenueTrend') }}</span>
              </div>
            </template>
            <div class="chart-placeholder">
              <p>{{ t('adminDashboard.chartLoading') }}</p>
              <p class="chart-data">{{ stats.chartData.revenue.map(v => (v / 1000000).toFixed(1) + 'M').join(', ') }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </AdminLayout>
</template>

<style scoped>
.dashboard-page {
  width: 100%;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
}

.page-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.summary-cards {
  margin-bottom: 32px;
}

.summary-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border-left: 4px solid;
  transition: transform 0.3s, box-shadow 0.3s;
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  font-size: 24px;
  margin-right: 16px;
}

.card-content {
  flex: 1;
}

.card-title {
  margin: 0 0 4px;
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-value {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.today-stats {
  margin-bottom: 32px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border-left: 4px solid var(--primary);
}

.stat-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--primary);
}

.charts-section {
  margin-bottom: 24px;
}

.chart-container {
  margin-bottom: 0;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  padding: 24px;
  background: var(--bg-primary);
  border-radius: 4px;
  color: var(--text-secondary);
}

.chart-placeholder p {
  margin: 8px 0;
  font-size: 14px;
}

.chart-data {
  font-size: 12px;
  color: var(--text-secondary);
  word-break: break-all;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 20px;
  }

  .card-value {
    font-size: 18px;
  }

  .stat-value {
    font-size: 16px;
  }
}
</style>
