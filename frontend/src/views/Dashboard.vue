<script setup>
import { onMounted, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";

import ThemeToggle from "@/components/ThemeToggle.vue";
import LanguageToggle from "@/components/LanguageToggle.vue";
import { listRoom } from "@/api/dashboard.api";

import { ElMessage } from "element-plus";
import { Calendar, OfficeBuilding } from "@element-plus/icons-vue";

const { t } = useI18n();

const allRooms = ref([]);
const searchForm = reactive({
  dateRange: [],
  guests: 2,
  bedType: "ALL",
});

const bedTypeOptions = [
  { value: "ALL", label: () => t("dashboard.allBeds") },
  { value: "SINGLE", label: () => t("dashboard.single") },
  { value: "DOUBLE", label: () => t("dashboard.double") },
];

const loadRooms = async () => {
  try {
    const res = await listRoom();
    allRooms.value = Array.isArray(res?.data) ? res.data : [];
  } catch (err) {
    allRooms.value = [];
    ElMessage.error(err?.message || t("common.internal_server_error"));
  }
};

const handleSearch = () => {
  ElMessage.success(
    t("dashboard.foundMessage", {
      count: filteredRooms.value.length,
      guests: searchForm.guests,
    }),
  );
};

const handleBook = (room) => {
  ElMessage({
    type: "success",
    message: t("dashboard.bookedMessage", {
      room: room.room_number,
      hotel: room.hotel || t("dashboard.logo"),
    }),
  });
};

onMounted(() => {
  loadRooms();
});
</script>

<template>
  <div class="hotel-page">
    <el-header class="main-header">
      <div class="header-inner">
        <div class="logo">{{ t("dashboard.logo") }}</div>

        <div class="header-right">
          <el-menu
            mode="horizontal"
            default-active="home"
            class="main-menu"
            ellipsis="false"
          >
            <el-menu-item index="home">{{ t("dashboard.home") }}</el-menu-item>
            <el-menu-item index="rooms">{{ t("dashboard.room") }}</el-menu-item>
          </el-menu>

          <div class="top-actions">
            <ThemeToggle />
            <LanguageToggle />
          </div>
        </div>
      </div>
    </el-header>

    <section class="hero-wrap">
      <div class="hero-content">
        <p class="hero-eyebrow">{{ t("dashboard.eyebrow") }}</p>
        <h1>{{ t("dashboard.title") }}</h1>
        <p class="hero-subtext">{{ t("dashboard.subtext") }}</p>

        <el-card class="search-card" shadow="always">
          <div class="search-grid">
            <div class="search-item">
              <label>{{ t("dashboard.dateLabel") }}</label>
              <el-date-picker
                v-model="searchForm.dateRange"
                type="daterange"
                :range-separator="t('dashboard.to')"
                :start-placeholder="t('dashboard.dateStart')"
                :end-placeholder="t('dashboard.dateEnd')"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :prefix-icon="Calendar"
              />
            </div>

            <div class="search-item">
              <label>{{ t("dashboard.bedType") }}</label>
              <el-select v-model="searchForm.bedType" style="width: 100%">
                <el-option
                  v-for="option in bedTypeOptions"
                  :key="option.value"
                  :label="option.label()"
                  :value="option.value"
                />
              </el-select>
            </div>

            <div class="search-item">
              <label>{{ t("dashboard.guests") }}</label>
              <el-input-number v-model="searchForm.guests" :min="1" :max="8" />
            </div>

            <el-button
              type="primary"
              class="search-button"
              size="large"
              @click="handleSearch"
            >
              {{ t("dashboard.search") }}
            </el-button>
          </div>
        </el-card>
      </div>
    </section>

    <section id="rooms" class="room-section">
      <div class="section-head">
        <h2>{{ t("dashboard.availableRooms") }}</h2>
        <p>
          {{ t("dashboard.showing") }} {{ allRooms.length }}
          {{ t("dashboard.roomUnit") }}
        </p>
      </div>

      <el-row :gutter="18">
        <el-col
          v-for="room in allRooms"
          :key="room.id"
          :xs="24"
          :sm="12"
          :lg="8"
        >
          <el-card class="room-card" shadow="hover">
            <img :src="room.image" :alt="room.room_number" class="room-image" />

            <div class="room-body">
              <h3>{{ t("dashboard.room") }}: {{ room.room_number }}</h3>

              <p class="hotel-name">
                <el-icon><OfficeBuilding /></el-icon>
                {{ t("dashboard.floor") }}: {{ room.floor }}
              </p>

              <p class="room-capacity">
                {{ t("dashboard.bedType") }}:
                {{
                  room.bed_type === "DOUBLE"
                    ? t("dashboard.double")
                    : t("dashboard.single")
                }}
              </p>

              <el-button
                type="primary"
                class="book-btn"
                @click="handleBook(room)"
              >
                {{ t("dashboard.bookNow") }}
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty
        v-if="allRooms.length === 0"
        :description="t('dashboard.empty')"
      />
    </section>
  </div>
</template>

<style scoped>
.hotel-page {
  min-height: 100vh;
  background: radial-gradient(
    circle at 20% 0%,
    rgba(204, 234, 255, 0.2) 0%,
    var(--bg-primary) 55%,
    var(--bg-primary) 100%
  );
  color: var(--text-primary);
}

.main-header {
  position: sticky;
  top: 0;
  z-index: 50;
  height: 60px;
  padding: 0;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.header-inner {
  max-width: 1120px;
  height: 100%;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.01em;
  color: var(--text-primary);
}

.main-menu {
  border-bottom: none;
  background: transparent;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hero-wrap {
  padding: 62px 16px 24px;
}

.hero-content {
  max-width: 960px;
  margin: 0 auto;
  text-align: center;
}

.hero-eyebrow {
  display: inline-block;
  margin: 0 0 10px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.15);
  color: var(--primary);
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.08em;
}

.hero-content h1 {
  margin: 0;
  font-size: clamp(30px, 5vw, 48px);
  line-height: 1.15;
}

.hero-subtext {
  margin: 14px auto 0;
  max-width: 620px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.search-card {
  margin: 28px auto 0;
  max-width: 980px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.search-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  gap: 12px;
  align-items: end;
}

.search-item {
  text-align: left;
}

.search-item label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: var(--text-secondary);
}

.search-button {
  height: 40px;
  border-radius: 10px;
  padding: 0 20px;
  font-weight: 700;
}

.room-section {
  max-width: 1120px;
  margin: 6px auto 0;
  padding: 0 16px 36px;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 14px;
}

.section-head h2 {
  margin: 0;
  font-size: clamp(24px, 3vw, 34px);
}

.section-head p {
  margin: 0;
  color: var(--text-secondary);
  font-weight: 600;
}

.room-card {
  border-radius: 14px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  margin-bottom: 16px;
  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease;
  background: var(--bg-secondary);
}

.room-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 24px rgba(18, 42, 79, 0.16);
}

.room-image {
  width: 100%;
  height: 210px;
  object-fit: cover;
}

.room-body {
  padding: 14px;
}

.room-body h3 {
  margin: 0 0 8px;
  color: var(--text-primary);
}

.hotel-name {
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  font-weight: 600;
}

.room-capacity {
  margin: 0 0 14px;
  color: var(--text-secondary);
}

.price strong {
  font-size: 28px;
  color: var(--primary);
  line-height: 1;
}

.price span {
  color: var(--text-secondary);
}

.book-btn {
  border: none;
  border-radius: 999px;
  font-weight: 700;
  padding: 10px 18px;
  background: linear-gradient(135deg, #0ea5e9, #2563eb);
  box-shadow: 0 8px 16px rgba(37, 99, 235, 0.28);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    filter 0.2s ease;
}

.book-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.03);
  box-shadow: 0 12px 20px rgba(37, 99, 235, 0.35);
}

@media (max-width: 980px) {
  .search-grid {
    grid-template-columns: 1fr 1fr;
  }

  .search-button {
    width: 100%;
  }
}

@media (max-width: 720px) {
  .header-inner {
    height: auto;
    min-height: 60px;
    padding-top: 8px;
    padding-bottom: 8px;
    flex-direction: column;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .search-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .main-header {
    height: auto;
  }

  .hero-wrap {
    padding-top: 38px;
  }

  .section-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
