<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import { ArrowLeft } from "@element-plus/icons-vue";

import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import { roomDetail } from "@/api/dashboard.api";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const loading = ref(false);
const guestLoading = ref(false);
const activeImageIndex = ref(0);

const detailRoom = ref({});
const bookingDates = ref([]);

const dialogState = reactive({
  visible: false,
  step: "question",
});

const guestState = reactive({
  guestList: [],
  selectedGuestId: null,
  createForm: {
    name: "",
    phone: "",
  },
});

const mockGallery = [
  "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80&sat=-20",
];

function getGuestList() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { id: 1, name: "Nguyen Van An", phone: "0901234567" },
        { id: 2, name: "Tran Minh Thu", phone: "0912345678" },
        { id: 3, name: "Le Hoang Nam", phone: "0987654321" },
      ]);
    }, 500);
  });
}

const roomImages = computed(() => {
  if (Array.isArray(detailRoom.value?.image) && detailRoom.value.image.length > 0) {
    return detailRoom.value.image;
  }

  return mockGallery;
});

const activeImage = computed(() => roomImages.value[activeImageIndex.value] || roomImages.value[0]);

const bedTypeLabel = computed(() => {
  if (detailRoom.value.bed_type === "DOUBLE") return t("room.bedTypeOptions.DOUBLE");
  if (detailRoom.value.bed_type === "SINGLE") return t("room.bedTypeOptions.SINGLE");
  return detailRoom.value.bed_type;
});

const guestFormRules = {
  name: [
    {
      required: true,
      message: t("booking.validation.nameRequired"),
      trigger: "blur",
    },
  ],
  phone: [
    {
      required: true,
      message: t("booking.validation.phoneRequired"),
      trigger: "blur",
    },
    {
      pattern: /^[0-9]{9,11}$/,
      message: t("booking.validation.phoneInvalid"),
      trigger: "blur",
    },
  ],
};

const guestFormRef = ref();

const fetchRoomDetail = async () => {
  loading.value = true;
  try {
    const res = await roomDetail(route.params.id);
    detailRoom.value = res?.data;
    detailRoom.value.image = mockGallery;
  } catch (err) {
    detailRoom.value = {};
    ElMessage.warning(err?.message || t("room.mockFallback"));
  } finally {
    loading.value = false;
  }
};

const isMaintenance = computed(() => detailRoom.value.status === "MAINTENANCE");

const statusLabel = computed(() => {
  const status = detailRoom.value?.status || 'MAINTENANCE'
  return t(`room.statusOptions.${status}`)
})

const resetDialogState = () => {
  dialogState.step = "question";
  guestState.guestList = [];
  guestState.selectedGuestId = null;
  guestState.createForm.name = "";
  guestState.createForm.phone = "";
  guestFormRef.value?.clearValidate();
};

const openBookingDialog = () => {
  if (roomState.bookingDates.length !== 2) {
    ElMessage.warning(t("booking.validation.dateRequired"));
    return;
  }

  dialogState.visible = true;
  resetDialogState();
};

const closeBookingDialog = () => {
  dialogState.visible = false;
  resetDialogState();
};

const selectGuestHistory = async () => {
  dialogState.step = "existing";
  guestLoading.value = true;

  try {
    guestState.guestList = await getGuestList();
  } catch (err) {
    guestState.guestList = [];
    ElMessage.error(err?.message || t("common.internal_server_error"));
  } finally {
    guestLoading.value = false;
  }
};

const selectNewGuest = () => {
  dialogState.step = "new";
};

const confirmExistingGuestBooking = () => {
  const selectedGuest = guestState.guestList.find(
    (guest) => guest.id === guestState.selectedGuestId,
  );

  if (!selectedGuest) {
    ElMessage.warning(t("booking.validation.selectGuest"));
    return;
  }

  ElMessage.success(
    t("booking.messages.confirmedExisting", {
      name: selectedGuest.name,
      room: room.value.room_number,
    }),
  );
  closeBookingDialog();
};

const createGuestAndBook = async () => {
  if (!guestFormRef.value) return;

  const valid = await guestFormRef.value.validate().catch(() => false);
  if (valid) {
    ElMessage.success(
      t("booking.messages.createdAndBooked", {
        name: guestState.createForm.name,
        room: room.value.room_number,
      }),
    );
    closeBookingDialog();
  }
};

onMounted(() => {
  fetchRoomDetail();
});

watch(
  roomImages,
  () => {
    activeImageIndex.value = 0;
  },
  { immediate: true },
);
</script>

<template>
  <div class="room-detail-page">
    <Header />

    <main class="detail-container">
      <div class="theme-orb theme-orb-left" />
      <div class="theme-orb theme-orb-right" />

      <el-button
        class="back-btn"
        circle
        plain
        :icon="ArrowLeft"
        :aria-label="t('common.returnBack')"
        :title="t('common.returnBack')"
        @click="router.push('/')"
      />

      <el-skeleton v-if="loading" animated>
        <template #template>
          <div class="skeleton-wrap">
            <el-skeleton-item variant="h1" style="width: 48%; height: 34px" />
            <el-skeleton-item
              variant="rect"
              style="width: 100%; height: 420px; margin-top: 18px"
            />
          </div>
        </template>
      </el-skeleton>

      <template v-else>
        <section class="detail-hero">
          <div class="hero-copy">
            <p class="eyebrow">{{ t("room.detailEyebrow") }}</p>
            <h1>
              {{ t("room.roomTitle", { roomNumber: detailRoom.room_number }) }}
            </h1>
          </div>

          <div class="hero-aside">
            <div class="hero-theme-card">
              <span>{{ t("room.bedType") }}</span>
              <strong>{{ bedTypeLabel }}</strong>
              <small>{{ t("room.floor") }} {{ detailRoom.floor }}</small>
            </div>
          </div>
        </section>

        <div class="detail-grid">
          <section class="gallery-card">
            <div class="gallery-layout">
              <el-image
                class="gallery-main"
                :src="activeImage"
                :preview-src-list="roomImages"
                :initial-index="activeImageIndex"
                fit="cover"
                preview-teleported
              />

              <div class="gallery-side">
                <el-image
                  v-for="(image, index) in roomImages.slice(1, 3)"
                  :key="`${image}-${index}`"
                  class="gallery-small"
                  :src="image"
                  :preview-src-list="roomImages"
                  :initial-index="index + 1"
                  fit="cover"
                  preview-teleported
                  @click="activeImageIndex = index + 1"
                />
              </div>
            </div>

            <div class="thumb-row">
              <button
                v-for="(image, index) in roomImages"
                :key="`thumb-${index}`"
                type="button"
                class="thumb-button"
                :class="{ active: activeImageIndex === index }"
                @click="activeImageIndex = index"
              >
                <img
                  :src="image"
                  :alt="t('room.galleryAlt', { index: index + 1 })"
                />
              </button>
            </div>
          </section>

          <div class="content-stack">
            <el-card class="info-card" shadow="hover">
              <template #header>
                <div class="card-head">
                  <div>
                    <p>{{ t("room.roomDetail") }}</p>
                    <h2>
                      {{
                        t("room.roomTitle", { roomNumber: detailRoom.room_number })
                      }}
                    </h2>
                  </div>
                </div>
              </template>

              <div class="info-grid">
                <div class="info-item">
                  <span>{{ t("room.bedType") }}</span>
                  <strong>{{ bedTypeLabel }}</strong>
                </div>

                <div class="info-item">
                  <span>{{ t("room.floor") }}</span>
                  <strong>{{ detailRoom.floor }}</strong>
                </div>

                <div class="info-item">
                  <span>{{ t("room.roomNumber") }}</span>
                  <strong>{{ detailRoom.room_number }}</strong>
                </div>

                <div class="info-item">
                  <span>{{ t("room.status") }}</span>
                  <strong>{{ statusLabel }}</strong>
                </div>
              </div>

              <div class="description-block">
                <h3>{{ t("room.description") }}</h3>
                <p>{{ detailRoom.description }}</p>
              </div>
            </el-card>

            <el-card
              v-if="isMaintenance"
              class="booking-card booking-disabled"
              shadow="never"
            >
              <h2>{{ t("booking.unavailableTitle") }}</h2>
              <p>{{ t("booking.unavailableDescription") }}</p>
            </el-card>

            <el-card class="booking-card" shadow="hover" v-else>
              <template #header>
                <div class="card-head">
                  <div>
                    <h2>{{ t("booking.sectionTitle") }}</h2>
                  </div>
                </div>
              </template>

              <p class="booking-text">{{ t("booking.sectionDescription") }}</p>

              <div class="booking-form">
                <label class="booking-label">{{
                  t("booking.dateRange")
                }}</label>
                <el-date-picker
                  v-model="bookingDates"
                  type="daterange"
                  class="booking-picker"
                  :range-separator="t('booking.to')"
                  :start-placeholder="t('booking.checkIn')"
                  :end-placeholder="t('booking.checkOut')"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />

                <el-button
                  type="primary"
                  size="large"
                  class="book-btn"
                  @click="openBookingDialog"
                >
                  {{ t("booking.bookNow") }}
                </el-button>
              </div>
            </el-card>
          </div>
        </div>
      </template>
    </main>

    <el-dialog
      v-model="dialogState.visible"
      :title="t('booking.dialog.title')"
      width="520px"
      class="booking-dialog"
      @closed="resetDialogState"
    >
      <div v-if="dialogState.step === 'question'" class="dialog-step">
        <p class="dialog-copy">{{ t("booking.dialog.question") }}</p>

        <div class="dialog-actions">
          <el-button type="primary" plain @click="selectGuestHistory">
            {{ t("booking.dialog.returningGuest") }}
          </el-button>
          <el-button type="primary" @click="selectNewGuest">
            {{ t("booking.dialog.newGuest") }}
          </el-button>
        </div>
      </div>

      <div v-else-if="dialogState.step === 'existing'" class="dialog-step">
        <p class="dialog-copy">{{ t("booking.dialog.selectGuest") }}</p>

        <el-skeleton v-if="guestLoading" animated :rows="3" />

        <el-radio-group
          v-else
          v-model="guestState.selectedGuestId"
          class="guest-list"
        >
          <el-radio
            v-for="guest in guestState.guestList"
            :key="guest.id"
            :label="guest.id"
            border
            class="guest-item"
          >
            <div class="guest-meta">
              <strong>{{ guest.name }}</strong>
              <span>{{ guest.phone }}</span>
            </div>
          </el-radio>
        </el-radio-group>
      </div>

      <div v-else class="dialog-step">
        <p class="dialog-copy">{{ t("booking.dialog.createGuest") }}</p>

        <el-form
          ref="guestFormRef"
          :model="guestState.createForm"
          :rules="guestFormRules"
          label-position="top"
        >
          <el-form-item :label="t('booking.form.name')" prop="name">
            <el-input
              v-model="guestState.createForm.name"
              :placeholder="t('booking.form.namePlaceholder')"
            />
          </el-form-item>

          <el-form-item :label="t('booking.form.phone')" prop="phone">
            <el-input
              v-model="guestState.createForm.phone"
              :placeholder="t('booking.form.phonePlaceholder')"
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeBookingDialog">
            {{ t("common.cancel") }}
          </el-button>

          <el-button
            v-if="dialogState.step === 'existing'"
            type="primary"
            @click="confirmExistingGuestBooking"
          >
            {{ t("booking.confirmBooking") }}
          </el-button>

          <el-button
            v-else-if="dialogState.step === 'new'"
            type="primary"
            @click="createGuestAndBook"
          >
            {{ t("booking.createAndBook") }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <Footer />
  </div>
</template>

<style scoped>
.room-detail-page {
  min-height: 100vh;
  background: var(--page-gradient);
}

.detail-container {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 16px 48px;
}

.back-btn {
  position: relative;
  z-index: 1;
  margin-bottom: 18px;
  border-radius: 999px;
  border-color: var(--border-color);
  background: color-mix(in srgb, var(--bg-secondary) 78%, transparent);
  color: var(--primary-hover);
  box-shadow: var(--shadow-soft);
}

.back-btn:hover {
  border-color: var(--primary);
  background: var(--card-surface);
  color: var(--primary-hover);
}

.skeleton-wrap {
  border-radius: 24px;
  background: var(--card-surface);
  padding: 24px;
}

.detail-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  padding: 28px;
  border: 1px solid var(--border-color);
  border-radius: 28px;
  background: var(--hero-surface);
  box-shadow: var(--shadow-strong);
  overflow: hidden;
  position: relative;
}

.detail-hero::after {
  content: "";
  position: absolute;
  inset: auto -60px -80px auto;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--primary) 18%, transparent),
    transparent 68%
  );
  pointer-events: none;
}

.hero-copy h1 {
  margin: 8px 0 12px;
  font-size: clamp(32px, 5vw, 54px);
  line-height: 1.05;
  color: var(--text-primary);
}

.eyebrow {
  display: inline-flex;
  margin: 0;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary-hover);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-text {
  max-width: 720px;
  margin: 0;
  color: var(--text-secondary);
  font-size: 16px;
  line-height: 1.7;
}

.hero-aside {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 12px;
  justify-items: end;
}

.hero-status {
  margin-top: 10px;
}

.hero-theme-card {
  min-width: 180px;
  padding: 16px 18px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  background: color-mix(in srgb, var(--bg-secondary) 86%, transparent);
  box-shadow: inset 0 1px 0 color-mix(in srgb, white 25%, transparent);
}

.hero-theme-card span,
.hero-theme-card small {
  display: block;
  color: var(--text-secondary);
}

.hero-theme-card strong {
  display: block;
  margin: 4px 0;
  color: var(--primary-hover);
  font-size: 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.9fr);
  gap: 24px;
  align-items: start;
}

.gallery-card,
.info-card,
.booking-card {
  border: 1px solid var(--border-color);
  border-radius: 24px;
  background: var(--card-surface);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(8px);
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color);
}

.gallery-card {
  padding: 18px;
}

.gallery-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(180px, 0.7fr);
  gap: 14px;
}

.gallery-main,
.gallery-small {
  overflow: hidden;
  border-radius: 20px;
  cursor: zoom-in;
}

.gallery-main {
  height: 440px;
}

.gallery-side {
  display: grid;
  gap: 14px;
}

.gallery-small {
  height: 213px;
}

.gallery-card :deep(.el-image__inner) {
  transition: transform 0.35s ease;
}

.gallery-main:hover :deep(.el-image__inner),
.gallery-small:hover :deep(.el-image__inner) {
  transform: scale(1.05);
}

.thumb-row {
  display: flex;
  gap: 10px;
  margin-top: 14px;
  flex-wrap: wrap;
}

.thumb-button {
  padding: 0;
  border: 2px solid transparent;
  border-radius: 14px;
  overflow: hidden;
  background: transparent;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.thumb-button img {
  display: block;
  width: 92px;
  height: 68px;
  object-fit: cover;
}

.thumb-button:hover,
.thumb-button.active {
  transform: translateY(-2px);
  border-color: var(--primary);
  box-shadow: 0 10px 20px color-mix(in srgb, var(--primary) 18%, transparent);
}

.content-stack {
  display: grid;
  gap: 20px;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  color: var(--text-secondary);
}

.card-head h2 {
  margin: 0;
  font-size: 26px;
  color: var(--text-primary);
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.info-item {
  padding: 16px;
  border-radius: 18px;
  background: linear-gradient(
    180deg,
    var(--bg-tertiary) 0%,
    color-mix(in srgb, var(--bg-tertiary) 82%, var(--bg-secondary)) 100%
  );
  border: 1px solid var(--border-color);
}

.info-item span {
  display: block;
  margin-bottom: 6px;
  color: var(--text-secondary);
  font-size: 13px;
}

.info-item strong {
  color: var(--text-primary);
  font-size: 16px;
}

.description-block {
  margin-top: 18px;
  padding: 18px;
  border-radius: 18px;
  background: var(--card-surface-muted);
}

.description-block h3 {
  margin: 0 0 10px;
  color: var(--text-primary);
  font-size: 18px;
}

.description-block p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.booking-text {
  margin: 0 0 16px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.booking-form {
  display: grid;
  gap: 14px;
}

.booking-label {
  color: var(--text-secondary);
  font-weight: 600;
}

.booking-picker {
  width: 100%;
}

.booking-card :deep(.el-input__wrapper),
.booking-card :deep(.el-select__wrapper),
.booking-card :deep(.el-range-editor.el-input__wrapper),
.booking-dialog :deep(.el-input__wrapper),
.booking-dialog :deep(.el-textarea__inner) {
  background: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
  color: var(--text-primary);
}

.book-btn {
  min-height: 46px;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  box-shadow: 0 14px 24px color-mix(in srgb, var(--primary) 26%, transparent);
}

.book-btn:hover {
  filter: brightness(1.04);
}

.booking-disabled h2 {
  margin: 0 0 10px;
  color: var(--text-primary);
}

.booking-disabled p {
  margin: 0;
  color: var(--text-secondary);
}

.dialog-copy {
  margin: 0 0 18px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.dialog-actions,
.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.guest-list {
  display: grid;
  gap: 12px;
}

.guest-item {
  margin-right: 0;
  width: 100%;
  height: auto;
  padding: 12px 14px;
  border-radius: 16px;
}

.guest-meta {
  display: grid;
  gap: 4px;
}

.guest-meta strong {
  color: var(--text-primary);
}

.guest-meta span {
  color: var(--text-secondary);
}

.theme-orb {
  position: absolute;
  border-radius: 999px;
  pointer-events: none;
  filter: blur(8px);
  opacity: 0.55;
}

.theme-orb-left {
  top: 90px;
  left: -30px;
  width: 140px;
  height: 140px;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--primary) 28%, transparent),
    transparent 72%
  );
}

.theme-orb-right {
  top: 180px;
  right: -10px;
  width: 180px;
  height: 180px;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--primary) 22%, transparent),
    transparent 68%
  );
}

.room-detail-page :deep(.el-card__body),
.room-detail-page :deep(.el-card__header),
.booking-dialog :deep(.el-dialog) {
  background: transparent;
}

.booking-dialog :deep(.el-dialog) {
  border: 1px solid var(--border-color);
  border-radius: 24px;
  background: var(--card-surface);
  box-shadow: var(--shadow-strong);
}

.booking-dialog :deep(.el-dialog__title) {
  color: var(--text-primary);
}

.booking-dialog :deep(.el-radio.is-bordered) {
  background: var(--bg-tertiary);
  border-color: var(--border-color);
}

@media (max-width: 1024px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .detail-hero {
    flex-direction: column;
    padding: 22px;
  }

  .hero-aside {
    width: 100%;
    justify-items: start;
  }

  .gallery-layout {
    grid-template-columns: 1fr;
  }

  .gallery-main {
    height: 320px;
  }

  .gallery-side {
    grid-template-columns: 1fr 1fr;
  }

  .gallery-small {
    height: 180px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 576px) {
  .detail-container {
    padding-top: 20px;
  }

  .back-btn {
    margin-bottom: 14px;
  }

  .hero-copy h1 {
    font-size: 30px;
  }

  .gallery-main {
    height: 240px;
  }

  .gallery-side {
    grid-template-columns: 1fr;
  }

  .gallery-small {
    height: 160px;
  }

  .thumb-button img {
    width: 78px;
    height: 58px;
  }
}
</style>
