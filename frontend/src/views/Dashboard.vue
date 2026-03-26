<script setup>
import { onMounted, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import { listRoom, searchRooms } from "@/api/dashboard.api";
import { disablePastDate } from "@/utils/date";

import { ElMessage } from "element-plus";
import { Calendar, OfficeBuilding } from "@element-plus/icons-vue";

const { t } = useI18n();
const router = useRouter();

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

const handleSearch = async () => {
  if (!searchForm.dateRange || searchForm.dateRange.length !== 2) {
    ElMessage.warning(t("dashboard.selectDateRange"));
    return;
  }

  try {
    const res = await searchRooms(
      searchForm.dateRange[0],
      searchForm.dateRange[1],
      searchForm.bedType
    );
    allRooms.value = Array.isArray(res?.data) ? res.data : [];
    ElMessage.success(
      t("dashboard.foundMessage", {
        count: allRooms.value.length,
        guests: searchForm.guests,
      })
    );
  } catch (err) {
    allRooms.value = [];
    ElMessage.error(err?.message || t("common.internal_server_error"));
  }
};

onMounted(() => {
  loadRooms();
});
</script>

<template>
  <div class="hotel-page">
    <Header />

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
                :disabled-date="disablePastDate"
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
                @click="router.push(`/rooms/${room.id}`)"
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

    <Footer />
  </div>
</template>

<style scoped>
.hotel-page {
  min-height: 100vh;
  background: var(--page-gradient);
  color: var(--text-primary);
}

.hero-wrap {
  position: relative;
  padding: 62px 16px 24px;
}

.hero-content {
  max-width: 960px;
  margin: 0 auto;
  text-align: center;
  padding: 30px 24px;
  border: 1px solid var(--border-color);
  border-radius: 28px;
  background: var(--hero-surface);
  box-shadow: var(--shadow-strong);
}

.hero-eyebrow {
  display: inline-block;
  margin: 0 0 10px;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
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
  border-radius: 22px;
  border: 1px solid var(--border-color);
  background: var(--card-surface);
  box-shadow: var(--shadow-soft);
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

.search-card :deep(.el-input__wrapper),
.search-card :deep(.el-select__wrapper),
.search-card :deep(.el-range-editor.el-input__wrapper),
.search-card :deep(.el-input-number),
.search-card :deep(.el-input-number__decrease),
.search-card :deep(.el-input-number__increase) {
  background: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
  color: var(--text-primary);
}

.search-button {
  height: 44px;
  border-radius: 14px;
  padding: 0 20px;
  font-weight: 700;
  border: none;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  box-shadow: 0 14px 24px color-mix(in srgb, var(--primary) 28%, transparent);
}

.search-button:hover {
  filter: brightness(1.04);
}

.room-section {
  max-width: 1120px;
  margin: 18px auto 0;
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
  border-radius: 22px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  margin-bottom: 16px;
  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease;
  background: var(--card-surface);
  box-shadow: var(--shadow-soft);
}

.room-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-strong);
}

.room-image {
  width: 100%;
  height: 210px;
  object-fit: cover;
}

.room-body {
  padding: 18px;
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
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  box-shadow: 0 12px 22px color-mix(in srgb, var(--primary) 26%, transparent);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    filter 0.2s ease;
}

.book-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.03);
  box-shadow: 0 16px 26px color-mix(in srgb, var(--primary) 32%, transparent);
}

.room-card :deep(.el-card__body),
.search-card :deep(.el-card__body) {
  background: transparent;
}

.hotel-page :deep(.el-empty__description p) {
  color: var(--text-secondary);
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
  .search-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero-wrap {
    padding-top: 38px;
  }

  .hero-content {
    padding: 22px 18px;
  }

  .section-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
