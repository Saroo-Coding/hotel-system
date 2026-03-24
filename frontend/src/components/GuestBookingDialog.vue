<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import { ArrowLeft } from "@element-plus/icons-vue";
import { createGuest, searchGuest } from "@/api/dashboard.api";

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  roomNumber: {
    type: [String, Number],
    default: "",
  },
});

const emit = defineEmits(["update:modelValue", "booked"]);

const { t } = useI18n();
const tr = (key, fallback) => {
  const value = t(key);
  return value === key ? fallback : value;
};

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

const currentStep = ref("search");
const loading = ref(false);
const searchKeyword = ref("");

const guestState = reactive({
  selectedGuest: null,
  foundGuestForm: {
    id: "",
    fullName: "",
    idType: "",
    idNumber: "",
    dateOfBirth: "",
    gender: "",
    nationality: "",
    phone: "",
    email: "",
  },
  createGuestForm: {
    fullName: "",
    idType: "CCCD",
    idNumber: "",
    dateOfBirth: "",
    gender: "MALE",
    nationality: "Vietnam",
    phone: "",
    email: "",
  },
});

const idTypeOptions = [
  { label: "CCCD", value: "CCCD" },
  { label: "Passport", value: "Passport" },
];

const genderOptions = computed(() => [
  { label: tr("booking.form.genderOptions.male", "Male"), value: "MALE" },
  { label: tr("booking.form.genderOptions.female", "Female"), value: "FEMALE" },
  { label: tr("booking.form.genderOptions.other", "Other"), value: "OTHER" },
]);

const fieldErrors = reactive({
  fullName: "",
  idType: "",
  idNumber: "",
  dateOfBirth: "",
  gender: "",
  nationality: "",
  phone: "",
  email: "",
});

const getErrorMessage = (error, fallback) => {
  if (typeof error?.message === "string" && error.message.trim()) {
    return tr(error.message, fallback);
  }
  if (typeof error?.detail === "string" && error.detail.trim()) {
    return tr(error.detail, fallback);
  }
  if (Array.isArray(error?.detail) && error.detail.length > 0) {
    const first = error.detail[0]?.msg || fallback;
    return tr(first, fallback);
  }
  return fallback;
};

const clearFieldErrors = () => {
  fieldErrors.fullName = "";
  fieldErrors.idType = "";
  fieldErrors.idNumber = "";
  fieldErrors.dateOfBirth = "";
  fieldErrors.gender = "";
  fieldErrors.nationality = "";
  fieldErrors.phone = "";
  fieldErrors.email = "";
};

const mapBackendFieldKey = {
  full_name: "fullName",
  id_type: "idType",
  id_number: "idNumber",
  date_of_birth: "dateOfBirth",
  gender: "gender",
  nationality: "nationality",
  phone: "phone",
  email: "email",
};

const applyBackendFieldErrors = (errorObj = {}) => {
  clearFieldErrors();
  Object.entries(errorObj).forEach(([backendKey, i18nKey]) => {
    const formKey = mapBackendFieldKey[backendKey];
    if (!formKey) return;
    fieldErrors[formKey] = tr(i18nKey, t("common.invalid_format"));
  });
};

const resetForms = () => {
  searchKeyword.value = "";
  guestState.selectedGuest = null;
  guestState.foundGuestForm.id = "";
  guestState.foundGuestForm.fullName = "";
  guestState.foundGuestForm.idType = "";
  guestState.foundGuestForm.idNumber = "";
  guestState.foundGuestForm.dateOfBirth = "";
  guestState.foundGuestForm.gender = "";
  guestState.foundGuestForm.nationality = "";
  guestState.foundGuestForm.phone = "";
  guestState.foundGuestForm.email = "";
  guestState.createGuestForm.fullName = "";
  guestState.createGuestForm.idType = "CCCD";
  guestState.createGuestForm.idNumber = "";
  guestState.createGuestForm.dateOfBirth = "";
  guestState.createGuestForm.gender = "MALE";
  guestState.createGuestForm.nationality = "Vietnam";
  guestState.createGuestForm.phone = "";
  guestState.createGuestForm.email = "";
  clearFieldErrors();
};

const resetDialogState = () => {
  currentStep.value = "search";
  loading.value = false;
  resetForms();
};

const closeDialog = () => {
  dialogVisible.value = false;
  resetDialogState();
};

const goBackToSearch = () => {
  currentStep.value = "search";
  resetForms();
};

const fillFoundGuest = (guest) => {
  guestState.selectedGuest = guest;
  guestState.foundGuestForm.id = guest.id;
  guestState.foundGuestForm.fullName = guest.full_name || "";
  guestState.foundGuestForm.idType = guest.id_type || "";
  guestState.foundGuestForm.idNumber = guest.id_number || "";
  guestState.foundGuestForm.dateOfBirth = guest.date_of_birth || "";
  guestState.foundGuestForm.gender = guest.gender || "";
  guestState.foundGuestForm.nationality = guest.nationality || "";
  guestState.foundGuestForm.phone = guest.phone || "";
  guestState.foundGuestForm.email = guest.email || "";
};

const handleSearchGuest = async () => {
  const keyword = searchKeyword.value.trim();
  loading.value = true;

  try {
    const res = await searchGuest(keyword);
    const foundGuest = res?.data;
    if (!foundGuest?.id) {
      throw new Error(t("booking.messages.guestNotFound"));
    }

    fillFoundGuest(foundGuest);
    currentStep.value = "existing";
  } catch (error) {
    const message = getErrorMessage(error, t("booking.messages.guestNotFound"));
    ElMessage.warning(message);
  } finally {
    loading.value = false;
  }
};

const goToCreateGuest = () => {
  currentStep.value = "create";
  const keyword = searchKeyword.value.trim();
  if (/^0[0-9]{9,10}$/.test(keyword)) {
    guestState.createGuestForm.phone = keyword;
  } else {
    guestState.createGuestForm.idNumber = keyword;
  }
};

const handleBookExistingGuest = async () => {
  if (!guestState.selectedGuest?.id) {
    ElMessage.warning(t("booking.validation.selectGuest"));
    return;
  }

  emit("booked", {
    type: "existing",
    guestId: guestState.selectedGuest.id,
    guest: { ...guestState.foundGuestForm },
  });
  closeDialog();
};

const handleCreateAndBook = async () => {
  loading.value = true;
  clearFieldErrors();
  try {
    const payload = {
      full_name: guestState.createGuestForm.fullName.trim(),
      id_type: guestState.createGuestForm.idType,
      id_number: guestState.createGuestForm.idNumber.trim(),
      date_of_birth: guestState.createGuestForm.dateOfBirth,
      gender: guestState.createGuestForm.gender,
      nationality: guestState.createGuestForm.nationality.trim(),
      phone: guestState.createGuestForm.phone.trim(),
      email: guestState.createGuestForm.email.trim(),
    };

    const res = await createGuest(payload);
    const createdGuestId = res?.data?.id;
    if (!createdGuestId) {
      throw new Error("common.internal_server_error");
    }

    emit("booked", {
      type: "new",
      guestId: createdGuestId,
      guest: { ...guestState.createGuestForm },
    });
    closeDialog();
  } catch (error) {
    if (error?.error && typeof error.error === "object") {
      applyBackendFieldErrors(error.error);
    }
    const message = getErrorMessage(error, t("common.internal_server_error"));
    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
};

watch(
  () => props.modelValue,
  (visible) => {
    if (!visible) {
      resetDialogState();
    }
  },
);
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    width="560px"
    class="guest-booking-dialog"
    :close-on-click-modal="false"
    @closed="resetDialogState"
  >
    <div class="dialog-shell">
      <div v-if="currentStep !== 'search'" class="step-back">
        <el-button
          circle
          plain
          :icon="ArrowLeft"
          :aria-label="t('common.returnBack')"
          :title="t('common.returnBack')"
          @click="goBackToSearch"
        />
      </div>

      <div v-if="currentStep === 'search'" class="dialog-step">
        <p class="dialog-copy">{{ t("booking.dialog.question") }}</p>

        <div class="search-block">
          <label class="field-label">{{ t("booking.search.label") }}</label>
          <el-input
            v-model="searchKeyword"
            :placeholder="t('booking.search.placeholder')"
            @keyup.enter="handleSearchGuest"
          />
        </div>

        <div class="dialog-footer">
          <!-- <el-button class="secondary-btn" @click="closeDialog">
            {{ t("booking.search.cancel") }}
          </el-button> -->
          <el-button class="secondary-btn" type="primary" plain @click="goToCreateGuest">
            {{ t("booking.search.create") }}
          </el-button>
          <el-button class="primary-btn" type="primary" :loading="loading" @click="handleSearchGuest">
            {{ t("booking.search.find") }}
          </el-button>
        </div>
      </div>

      <div v-else-if="currentStep === 'existing'" class="dialog-step">
        <p class="dialog-copy">{{ t("booking.dialog.selectGuest") }}</p>

        <el-form :model="guestState.foundGuestForm" label-position="top">
          <el-form-item :label="t('booking.form.name')">
            <el-input v-model="guestState.foundGuestForm.fullName" readonly />
          </el-form-item>

          <el-form-item :label="tr('booking.form.idType', 'ID type')">
            <el-input v-model="guestState.foundGuestForm.idType" readonly />
          </el-form-item>

          <el-form-item :label="t('booking.form.citizenId')">
            <el-input v-model="guestState.foundGuestForm.idNumber" readonly />
          </el-form-item>

          <el-form-item :label="t('booking.form.phone')">
            <el-input v-model="guestState.foundGuestForm.phone" readonly />
          </el-form-item>

          <el-form-item :label="tr('booking.form.email', 'Email')">
            <el-input v-model="guestState.foundGuestForm.email" readonly />
          </el-form-item>
        </el-form>

        <div class="dialog-footer dialog-footer-right">
          <el-button class="primary-btn" type="primary" :loading="loading" @click="handleBookExistingGuest">
            {{ t("booking.book") }}
          </el-button>
        </div>
      </div>

      <div v-else class="dialog-step">
        <p class="dialog-copy">{{ t("booking.dialog.createGuest") }}</p>

        <el-form
          :model="guestState.createGuestForm"
          label-position="top"
        >
          <el-form-item :label="t('booking.form.name')" :error="fieldErrors.fullName">
            <el-input
              v-model="guestState.createGuestForm.fullName"
              :placeholder="t('booking.form.namePlaceholder')"
            />
          </el-form-item>

          <el-form-item :label="tr('booking.form.idType', 'ID type')" :error="fieldErrors.idType">
            <el-select v-model="guestState.createGuestForm.idType" style="width: 100%">
              <el-option
                v-for="option in idTypeOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item :label="t('booking.form.citizenId')" :error="fieldErrors.idNumber">
            <el-input
              v-model="guestState.createGuestForm.idNumber"
              :placeholder="t('booking.form.citizenIdPlaceholder')"
            />
          </el-form-item>

          <el-form-item :label="t('booking.form.phone')" :error="fieldErrors.phone">
            <el-input
              v-model="guestState.createGuestForm.phone"
              :placeholder="t('booking.form.phonePlaceholder')"
            />
          </el-form-item>

          <el-form-item :label="tr('booking.form.email', 'Email')" :error="fieldErrors.email">
            <el-input
              v-model="guestState.createGuestForm.email"
              :placeholder="tr('booking.form.emailPlaceholder', 'Enter email')"
            />
          </el-form-item>

          <el-form-item :label="tr('booking.form.dateOfBirth', 'Date of birth')" :error="fieldErrors.dateOfBirth">
            <el-date-picker
              v-model="guestState.createGuestForm.dateOfBirth"
              type="date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
              :placeholder="tr('booking.form.dateOfBirthPlaceholder', 'Select date of birth')"
            />
          </el-form-item>

          <el-form-item :label="tr('booking.form.gender', 'Gender')" :error="fieldErrors.gender">
            <el-select v-model="guestState.createGuestForm.gender" style="width: 100%">
              <el-option
                v-for="option in genderOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item :label="tr('booking.form.nationality', 'Nationality')" :error="fieldErrors.nationality">
            <el-input
              v-model="guestState.createGuestForm.nationality"
              :placeholder="tr('booking.form.nationalityPlaceholder', 'Enter nationality')"
            />
          </el-form-item>
        </el-form>

        <div class="dialog-footer dialog-footer-right">
          <el-button class="primary-btn" type="primary" :loading="loading" @click="handleCreateAndBook">
            {{ t("booking.createAndBook") }}
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<style scoped>
.dialog-shell {
  position: relative;
}

.step-back {
  margin-bottom: 12px;
}

.dialog-copy {
  margin: 0 0 18px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.search-block {
  display: grid;
  gap: 8px;
}

.field-label {
  color: var(--text-secondary);
  font-weight: 600;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  flex-wrap: wrap;
  margin-top: 20px;
}

.dialog-footer-right {
  justify-content: flex-end;
}

.guest-booking-dialog :deep(.el-dialog) {
  border: 1px solid rgba(172, 119, 63, 0.18);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 24px 50px rgba(93, 58, 31, 0.14);
}

.guest-booking-dialog :deep(.el-dialog__title) {
  color: #1f2a37;
}

.guest-booking-dialog :deep(.el-input__wrapper) {
  background: rgba(255, 249, 242, 0.9);
  box-shadow: 0 0 0 1px rgba(172, 119, 63, 0.18) inset;
  color: #1f2a37;
}

.primary-btn {
  border: none;
  border-radius: 14px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  box-shadow: 0 14px 24px color-mix(in srgb, var(--primary) 26%, transparent);
}

.primary-btn:hover {
  filter: brightness(1.04);
}

.secondary-btn {
  border-radius: 14px;
  font-weight: 600;
}

.guest-booking-dialog :deep(.el-button--primary.is-plain.secondary-btn) {
  border-color: rgba(201, 123, 54, 0.28);
  background: rgba(255, 249, 242, 0.92);
  color: var(--primary-hover);
}

.guest-booking-dialog :deep(.el-button--default.secondary-btn) {
  border-color: rgba(172, 119, 63, 0.18);
  background: rgba(255, 255, 255, 0.92);
  color: #5f6f82;
}

@media (max-width: 576px) {
  .dialog-footer {
    justify-content: stretch;
  }

  .dialog-footer :deep(.el-button) {
    width: 100%;
  }
}
</style>
