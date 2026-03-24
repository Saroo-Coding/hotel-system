<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import { cancelBooking, searchBookingByCode } from "@/api/dashboard.api";

const route = useRoute();
const router = useRouter();
const { t, locale } = useI18n();

const countdown = ref(0);
let timer = null;
const selectedPaymentMethod = ref("bank_transfer");
const loading = ref(false);
const searchCode = ref("");
const bookingData = ref({
  id: "",
  code: "",
  status: "PENDING",
  paymentStatus: "PENDING",
  checkinDate: "",
  checkoutDate: "",
  totalPrice: "",
});

const bookingCode = computed(() => String(route.params.bookingCode || "").trim().toUpperCase());
const hasResult = computed(() => Boolean(bookingData.value.id));
const isPending = computed(() => bookingData.value.status === "PENDING");

const formatDate = (value) => {
  if (!value) return "--";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return new Intl.DateTimeFormat(locale.value === "vi" ? "vi-VN" : "en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(parsed);
};

const formatCurrency = (value) => {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "--";
  return new Intl.NumberFormat(locale.value === "vi" ? "vi-VN" : "en-US").format(amount);
};

const statusLabel = computed(() => t(`booking.pending.statusOptions.${bookingData.value.status}`));
const paymentLabel = computed(() =>
  t(`booking.pending.paymentOptions.${bookingData.value.paymentStatus}`),
);
const statusDescription = computed(
  () => t(`booking.lookup.statusDescriptions.${bookingData.value.status}`),
);

const countdownDisplay = computed(() => {
  const minutes = Math.floor(countdown.value / 60);
  const seconds = countdown.value % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
});

const paymentMethods = computed(() => [
  {
    id: "bank_transfer",
    badge: "BANK",
    name: t("booking.pending.methodOptions.bank_transfer"),
    description: t("booking.pending.methodDescriptions.bank_transfer"),
  },
  {
    id: "credit_card",
    badge: "CARD",
    name: t("booking.pending.methodOptions.credit_card"),
    description: t("booking.pending.methodDescriptions.credit_card"),
  },
  {
    id: "e_wallet",
    badge: "WALLET",
    name: t("booking.pending.methodOptions.e_wallet"),
    description: t("booking.pending.methodDescriptions.e_wallet"),
  },
]);

const fakePaymentDetails = computed(() => {
  if (selectedPaymentMethod.value === "credit_card") {
    return [
      {
        label: t("booking.pending.fake.fields.cardHolder"),
        value: t("booking.pending.fakeValues.cardHolder"),
      },
      {
        label: t("booking.pending.fake.fields.cardNumber"),
        value: t("booking.pending.fakeValues.cardNumber"),
      },
      {
        label: t("booking.pending.fake.fields.gateway"),
        value: t("booking.pending.fakeValues.gateway"),
      },
    ];
  }

  if (selectedPaymentMethod.value === "e_wallet") {
    return [
      {
        label: t("booking.pending.fake.fields.walletProvider"),
        value: t("booking.pending.fakeValues.walletProvider"),
      },
      {
        label: t("booking.pending.fake.fields.walletId"),
        value: t("booking.pending.fakeValues.walletId"),
      },
      {
        label: t("booking.pending.fake.fields.walletPhone"),
        value: t("booking.pending.fakeValues.walletPhone"),
      },
    ];
  }

  return [
    {
      label: t("booking.pending.fake.fields.accountName"),
      value: t("booking.pending.fakeValues.accountName"),
    },
    {
      label: t("booking.pending.fake.fields.accountNumber"),
      value: t("booking.pending.fakeValues.accountNumber"),
    },
    {
      label: t("booking.pending.fake.fields.bankName"),
      value: t("booking.pending.fakeValues.bankName"),
    },
  ];
});

const goHome = () => router.replace("/");

const toI18nMessage = (err, fallbackKey) => {
  if (typeof err?.message === "string" && err.message.trim()) {
    return t(err.message);
  }
  if (typeof err?.detail === "string" && err.detail.trim()) {
    return t(err.detail);
  }
  return t(fallbackKey);
};

const loadBookingPending = async (code) => {
  const normalizedCode = String(code || "").trim().toUpperCase();
  if (!normalizedCode) return;

  if (timer) {
    clearInterval(timer);
    timer = null;
  }

  loading.value = true;
  try {
    const res = await searchBookingByCode(normalizedCode);
    bookingData.value = {
      id: res?.id || "",
      code: res?.booking_code || normalizedCode,
      status: res?.status || "PENDING",
      paymentStatus: res?.payment_status || "PENDING",
      checkinDate: res?.checkin_date || "",
      checkoutDate: res?.checkout_date || "",
      totalPrice: String(res?.total_price ?? ""),
    };
    countdown.value = Number(res?.remaining_seconds || 0);
  } catch (err) {
    ElMessage.error(toI18nMessage(err, "common.internal_server_error"));
    bookingData.value = {
      id: "",
      code: "",
      status: "PENDING",
      paymentStatus: "PENDING",
      checkinDate: "",
      checkoutDate: "",
      totalPrice: "",
    };
    countdown.value = 0;
    return;
  } finally {
    loading.value = false;
  }

  if (!bookingData.value.id) return;

  if (!isPending.value) return;
  if (countdown.value <= 0) return;

  timer = setInterval(() => {
    countdown.value -= 1;
    if (countdown.value <= 0) {
      clearInterval(timer);
      goHome();
    }
  }, 1000);
};

const handleSearch = async () => {
  const normalizedCode = String(searchCode.value || "").trim().toUpperCase();
  if (!normalizedCode) {
    ElMessage.warning(t("booking.lookup.searchRequired"));
    return;
  }

  if (normalizedCode === bookingCode.value) {
    await loadBookingPending(normalizedCode);
    return;
  }

  router.push({ name: "my-room-code", params: { bookingCode: normalizedCode } });
};

const handleCancelBooking = async () => {
  if (!bookingData.value.code || !isPending.value) return;

  try {
    await ElMessageBox.confirm(
      t("booking.lookup.cancelConfirm"),
      t("booking.lookup.cancel"),
      {
        confirmButtonText: t("booking.lookup.cancel"),
        cancelButtonText: t("common.cancel"),
        type: "warning",
      },
    );

    const res = await cancelBooking(bookingData.value.code);
    ElMessage.success(t(res?.message || "booking.lookup.cancelSuccess"));
    bookingData.value = {
      id: "",
      code: "",
      status: "PENDING",
      paymentStatus: "PENDING",
      checkinDate: "",
      checkoutDate: "",
      totalPrice: "",
    };
    countdown.value = 0;
    searchCode.value = "";
    router.push({ name: "my-room" });
  } catch (err) {
    if (err === "cancel") return;
    ElMessage.error(toI18nMessage(err, "common.internal_server_error"));
  }
};

onMounted(() => {
  if (bookingCode.value) {
    searchCode.value = bookingCode.value;
    loadBookingPending(bookingCode.value);
    return;
  }
  loading.value = false;
});

watch(
  () => route.params.bookingCode,
  (newValue) => {
    const normalizedCode = String(newValue || "").trim().toUpperCase();
    if (!normalizedCode) return;
    searchCode.value = normalizedCode;
    loadBookingPending(normalizedCode);
  },
);

onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
});
</script>

<template>
  <div class="pending-page">
    <Header />

    <main class="pending-container">
      <div class="theme-orb theme-orb-left" />
      <div class="theme-orb theme-orb-right" />

      <section class="pending-card" v-loading="loading">
        <p class="eyebrow">{{ t("booking.lookup.eyebrow") }}</p>
        <h1>{{ t("booking.lookup.title") }}</h1>
        <p class="description">{{ t("booking.lookup.description") }}</p>

        <div class="search-bar">
          <el-input
            v-model="searchCode"
            :placeholder="t('booking.lookup.placeholder')"
            size="large"
            clearable
            @keyup.enter="handleSearch"
          />
          <el-button type="primary" size="large" class="search-btn" @click="handleSearch">
            {{ t("booking.lookup.search") }}
          </el-button>
        </div>

        <div v-if="hasResult && isPending" class="countdown-badge">
          {{ t("booking.pending.redirectIn", { time: countdownDisplay }) }}
        </div>

        <el-empty v-if="!hasResult && !loading" :description="t('booking.lookup.empty')" />

        <div v-if="hasResult" class="pending-layout">
          <div class="panel">
            <h2 class="panel-title">{{ t("booking.pending.bookingInfoTitle") }}</h2>
            <div class="info-grid">
              <div class="info-item">
                <span>{{ t("booking.pending.bookingCode") }}</span>
                <strong>{{ bookingData.code }}</strong>
              </div>

              <div class="info-item">
                <span>{{ t("booking.pending.bookingStatus") }}</span>
                <strong>{{ statusLabel }}</strong>
              </div>

              <div class="info-item">
                <span>{{ t("booking.pending.checkinDate") }}</span>
                <strong>{{ formatDate(bookingData.checkinDate) }}</strong>
              </div>

              <div class="info-item">
                <span>{{ t("booking.pending.checkoutDate") }}</span>
                <strong>{{ formatDate(bookingData.checkoutDate) }}</strong>
              </div>

              <div class="info-item">
                <span>{{ t("booking.pending.paymentStatus") }}</span>
                <strong>{{ paymentLabel }}</strong>
              </div>
            </div>
          </div>

          <div v-if="isPending" class="panel payment-panel">
            <h2 class="panel-title">{{ t("booking.pending.paymentTitle") }}</h2>
            <div class="total-box">
              <span>{{ t("booking.pending.totalPrice") }}</span>
              <strong>{{ formatCurrency(bookingData.totalPrice) }} VND</strong>
            </div>

            <p class="method-label">{{ t("booking.pending.paymentMethod") }}</p>
            <div class="method-list">
              <button
                v-for="method in paymentMethods"
                :key="method.id"
                type="button"
                class="method-card"
                :class="{ active: selectedPaymentMethod === method.id }"
                @click="selectedPaymentMethod = method.id"
              >
                <span class="method-badge">{{ method.badge }}</span>
                <span class="method-content">
                  <strong>{{ method.name }}</strong>
                  <small>{{ method.description }}</small>
                </span>
              </button>
            </div>

            <div class="fake-payment">
              <p class="fake-title">{{ t("booking.pending.fake.title") }}</p>
              <div class="fake-row" v-for="(item, index) in fakePaymentDetails" :key="index">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </div>

          <div v-else class="panel status-panel">
            <h2 class="panel-title">{{ t("booking.lookup.statusTitle") }}</h2>
            <div class="status-box">
              <p>{{ statusDescription }}</p>
              <strong>{{ statusLabel }}</strong>
            </div>

            <div class="total-box">
              <span>{{ t("booking.pending.totalPrice") }}</span>
              <strong>{{ formatCurrency(bookingData.totalPrice) }} VND</strong>
            </div>
          </div>
        </div>

        <div v-if="hasResult && isPending" class="bottom-actions">
          <el-button type="danger" plain class="cancel-btn" @click="handleCancelBooking">
            {{ t("booking.lookup.cancel") }}
          </el-button>
        </div>
      </section>
    </main>

    <Footer />
  </div>
</template>

<style scoped>
.pending-page {
  min-height: 100vh;
  background: var(--page-gradient);
}

.pending-container {
  position: relative;
  max-width: 1120px;
  margin: 0 auto;
  padding: 40px 16px 56px;
}

.pending-card {
  position: relative;
  z-index: 1;
  margin: 22px auto 0;
  max-width: 880px;
  padding: clamp(24px, 4vw, 40px);
  border-radius: 28px;
  border: 1px solid var(--border-color);
  background: var(--hero-surface);
  box-shadow: var(--shadow-strong);
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

h1 {
  margin: 14px 0 8px;
  color: var(--text-primary);
  font-size: clamp(28px, 4vw, 40px);
}

.description {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.countdown-badge {
  display: inline-flex;
  margin-top: 16px;
  padding: 8px 14px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--primary) 16%, transparent);
  color: var(--primary-hover);
  font-weight: 700;
}

.search-bar {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  margin-top: 16px;
}

.search-btn {
  border: none;
  border-radius: 12px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
}

.bottom-actions {
  margin-top: 18px;
  display: flex;
  justify-content: flex-end;
}

.cancel-btn {
  border-radius: 12px;
  font-weight: 700;
}

.pending-layout {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 14px;
  margin-top: 20px;
}

.panel {
  padding: 14px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
  background: var(--card-surface);
}

.panel-title {
  margin: 0 0 12px;
  color: var(--text-primary);
  font-size: 18px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.info-item {
  padding: 14px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
  background: var(--card-surface);
}

.info-item span {
  display: block;
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 6px;
}

.info-item strong {
  color: var(--text-primary);
}

.payment-panel {
  display: grid;
  align-content: start;
  gap: 14px;
}

.status-panel {
  display: grid;
  align-content: start;
  gap: 14px;
}

.status-box {
  padding: 14px;
  border-radius: 14px;
  border: 1px solid var(--border-color);
  background: color-mix(in srgb, var(--primary) 7%, var(--card-surface));
}

.status-box p {
  margin: 0 0 8px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.status-box strong {
  color: var(--primary-hover);
  font-size: 18px;
}

.total-box {
  padding: 14px;
  border-radius: 14px;
  border: 1px solid var(--border-color);
  background: color-mix(in srgb, var(--primary) 8%, var(--card-surface));
}

.total-box span {
  display: block;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.total-box strong {
  color: var(--primary-hover);
  font-size: 24px;
}

.method-label {
  margin: 0;
  color: var(--text-secondary);
  font-weight: 600;
}

.method-list {
  display: grid;
  gap: 8px;
}

.method-card {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-tertiary);
  cursor: pointer;
  text-align: left;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.method-card:hover {
  border-color: color-mix(in srgb, var(--primary) 65%, var(--border-color));
  transform: translateY(-1px);
}

.method-card.active {
  border-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, var(--card-surface));
  box-shadow: 0 10px 18px color-mix(in srgb, var(--primary) 18%, transparent);
}

.method-badge {
  min-width: 58px;
  padding: 6px 8px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  text-align: center;
  letter-spacing: 0.05em;
}

.method-content strong {
  display: block;
  color: var(--text-primary);
}

.method-content small {
  display: block;
  color: var(--text-secondary);
  margin-top: 2px;
}

.fake-payment {
  margin-top: 4px;
  padding: 12px;
  border-radius: 12px;
  border: 1px dashed color-mix(in srgb, var(--primary) 35%, var(--border-color));
  background: color-mix(in srgb, var(--primary) 5%, var(--card-surface));
}

.fake-title {
  margin: 0 0 8px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
}

.fake-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 6px 0;
  border-bottom: 1px solid color-mix(in srgb, var(--border-color) 82%, transparent);
}

.fake-row:last-child {
  border-bottom: none;
}

.fake-row span {
  color: var(--text-secondary);
  font-size: 13px;
}

.fake-row strong {
  color: var(--text-primary);
  font-size: 13px;
}

.theme-orb {
  position: absolute;
  border-radius: 999px;
  pointer-events: none;
  filter: blur(8px);
  opacity: 0.55;
}

.theme-orb-left {
  top: 100px;
  left: -20px;
  width: 150px;
  height: 150px;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--primary) 28%, transparent),
    transparent 72%
  );
}

.theme-orb-right {
  top: 210px;
  right: -18px;
  width: 190px;
  height: 190px;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--primary) 22%, transparent),
    transparent 70%
  );
}

@media (max-width: 768px) {
  .search-bar {
    grid-template-columns: 1fr;
  }

  .pending-layout {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
