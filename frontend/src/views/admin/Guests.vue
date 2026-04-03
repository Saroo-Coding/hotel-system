<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { deleteAdminGuest, getAdminGuestDetail, listAdminGuests, restoreAdminGuest, updateAdminGuest } from '@/api/dashboard.api';
import { Edit, Lock, Refresh, Delete, CircleCheck } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useAuthStore } from '@/stores/auth.store';

const { t } = useI18n();
const authStore = useAuthStore();

const guests = ref([]);
const loading = ref(false);
const submitting = ref(false);
const keyword = ref('');

const dialogVisible = ref(false);
const formRef = ref(null);

const currentRole = computed(() => authStore.user?.role || '');
const canManageGuests = computed(() => currentRole.value === 'ADMIN' || currentRole.value === 'STAFF');
const canRestoreGuest = computed(() => currentRole.value === 'ADMIN');
const hasGuestActions = computed(() => canManageGuests.value || canRestoreGuest.value);

const defaultGuestForm = () => ({
  id: '',
  full_name: '',
  id_type: 'CCCD',
  id_number: '',
  date_of_birth: '',
  gender: 'MALE',
  nationality: '',
  phone: '',
  email: '',
});

const guestForm = reactive(defaultGuestForm());

const formRules = computed(() => ({
  full_name: [{ required: true, message: t('booking.validation.nameRequired'), trigger: 'blur' }],
  id_type: [{ required: true, message: t('booking.validation.idTypeRequired'), trigger: 'change' }],
  id_number: [{ required: true, message: t('booking.validation.citizenIdRequired'), trigger: 'blur' }],
  date_of_birth: [{ required: true, message: t('booking.validation.dateOfBirthRequired'), trigger: 'change' }],
  gender: [{ required: true, message: t('booking.validation.genderRequired'), trigger: 'change' }],
  phone: [{ required: true, message: t('booking.validation.phoneRequired'), trigger: 'blur' }],
}));

const normalizeDateValue = (value) => {
  if (!value) return '';
  if (typeof value === 'string') return value.slice(0, 10);
  return value;
};

const getErrorMessage = (error, fallbackKey = 'common.internal_server_error') => {
  if (typeof error?.detail === 'string') return t(error.detail);
  if (error?.error && typeof error.error === 'object') {
    const firstField = Object.values(error.error)[0];
    if (typeof firstField === 'string') return t(firstField);
  }
  if (error?.detail && typeof error.detail === 'object') {
    const firstField = Object.values(error.detail)[0];
    if (typeof firstField === 'string') return t(firstField);
  }
  return t(fallbackKey);
};

const resetGuestForm = () => {
  Object.assign(guestForm, defaultGuestForm());
};

const fetchGuests = async () => {
  loading.value = true;
  try {
    const response = await listAdminGuests({
      page: 1,
      limit: 100,
      keyword: keyword.value,
    });
    guests.value = response.data || [];
  } catch (error) {
    ElMessage.error(getErrorMessage(error));
  } finally {
    loading.value = false;
  }
};

const openEditDialog = async (guest) => {
  if (!canManageGuests.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }
  try {
    loading.value = true;
    const response = await getAdminGuestDetail(guest.id);
    const detail = response.data || {};
    Object.assign(guestForm, {
      id: detail.id,
      full_name: detail.full_name || '',
      id_type: detail.id_type || 'CCCD',
      id_number: detail.id_number || '',
      date_of_birth: normalizeDateValue(detail.date_of_birth),
      gender: detail.gender || 'MALE',
      nationality: detail.nationality || '',
      phone: detail.phone || '',
      email: detail.email || '',
    });
    dialogVisible.value = true;
  } catch (error) {
    ElMessage.error(getErrorMessage(error));
  } finally {
    loading.value = false;
  }
};

const submitGuestForm = async () => {
  if (!canManageGuests.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }

  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitting.value = true;
  try {
    const payload = {
      full_name: guestForm.full_name?.trim(),
      id_type: guestForm.id_type,
      id_number: guestForm.id_number?.trim(),
      date_of_birth: guestForm.date_of_birth,
      gender: guestForm.gender,
      nationality: guestForm.nationality?.trim() || null,
      phone: guestForm.phone?.trim(),
      email: guestForm.email?.trim() || null,
    };
    await updateAdminGuest(guestForm.id, payload);
    ElMessage.success(t('guests.updated'));
    dialogVisible.value = false;
    resetGuestForm();
    await fetchGuests();
  } catch (error) {
    ElMessage.error(getErrorMessage(error));
  } finally {
    submitting.value = false;
  }
};

const handleDelete = async (guest) => {
  if (!canManageGuests.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }
  if (guest.del_flag) return;

  try {
    await ElMessageBox.confirm(
      t('guests.confirmDelete', { name: guest.full_name }),
      t('common.warning'),
      {
        confirmButtonText: t('common.ok'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
      }
    );
    loading.value = true;
    await deleteAdminGuest(guest.id);
    ElMessage.success(t('common.deleted'));
    await fetchGuests();
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(getErrorMessage(error));
    }
  } finally {
    loading.value = false;
  }
};

const handleRestore = async (guest) => {
  if (!canRestoreGuest.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }
  if (!guest.del_flag) return;

  try {
    await ElMessageBox.confirm(
      t('guests.confirmRestore', { name: guest.full_name }),
      t('common.warning'),
      {
        confirmButtonText: t('common.ok'),
        cancelButtonText: t('common.cancel'),
        type: 'success',
      }
    );
    loading.value = true;
    await restoreAdminGuest(guest.id);
    ElMessage.success(t('guests.restored'));
    await fetchGuests();
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(getErrorMessage(error));
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchGuests();
});
</script>

<template>
  <AdminLayout>
    <div class="guests-page">
      <div class="page-header">
        <h1>{{ t('admin.guests') }}</h1>
        <div class="actions">
          <el-input v-model="keyword" clearable :placeholder="t('dashboard.search')" style="width: 220px" @keyup.enter="fetchGuests" />
          <el-button :icon="Refresh" @click="fetchGuests">{{ t('rooms.refresh') }}</el-button>
        </div>
      </div>

      <el-table :data="guests" stripe border class="guests-table" v-loading="loading">
        <el-table-column prop="full_name" :label="t('guests.fullName')" min-width="180" />
        <el-table-column prop="id_number" :label="t('booking.form.citizenId')" min-width="140" />
        <el-table-column prop="phone" :label="t('guests.phone')" width="140" />
        <el-table-column prop="email" :label="t('guests.email')" min-width="180" />
        <el-table-column prop="created_at" :label="t('guests.createdAt')" width="160" />
        <el-table-column :label="t('guests.status')" width="130" align="center">
          <template #default="{ row }">
            <el-tag :type="row.del_flag ? 'info' : 'success'" effect="plain">
              {{ row.del_flag ? t('guests.deleted') : t('guests.active') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="hasGuestActions" :label="t('common.actions')" width="170" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="canManageGuests && !row.del_flag"
              size="large"
              class="action-btn"
              type="primary"
              :icon="Edit"
              @click="openEditDialog(row)"
              text
            />
            <el-button
              v-if="canManageGuests && !row.del_flag"
              size="large"
              class="action-btn"
              type="danger"
              :icon="Delete"
              @click="handleDelete(row)"
              text
            />
            <el-button
              v-else-if="canRestoreGuest && row.del_flag"
              size="large"
              class="action-btn"
              type="success"
              :icon="CircleCheck"
              @click="handleRestore(row)"
              text
            />
            <el-button v-else-if="row.del_flag" size="large" class="action-btn" type="info" :icon="Lock" disabled text />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="t('guests.editGuest')"
      width="640px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="guestForm" :rules="formRules" label-position="top">
        <el-form-item :label="t('guests.fullName')" prop="full_name">
          <el-input v-model="guestForm.full_name" />
        </el-form-item>
        <el-form-item :label="t('booking.form.idType')" prop="id_type">
          <el-select v-model="guestForm.id_type">
            <el-option label="CCCD" value="CCCD" />
            <el-option label="Passport" value="Passport" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('booking.form.citizenId')" prop="id_number">
          <el-input v-model="guestForm.id_number" />
        </el-form-item>
        <el-form-item :label="t('guests.dateOfBirth')" prop="date_of_birth">
          <el-date-picker v-model="guestForm.date_of_birth" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('booking.form.gender')" prop="gender">
          <el-select v-model="guestForm.gender">
            <el-option label="MALE" value="MALE" />
            <el-option label="FEMALE" value="FEMALE" />
            <el-option label="OTHER" value="OTHER" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('booking.form.nationality')">
          <el-input v-model="guestForm.nationality" />
        </el-form-item>
        <el-form-item :label="t('guests.phone')" prop="phone">
          <el-input v-model="guestForm.phone" />
        </el-form-item>
        <el-form-item :label="t('guests.email')">
          <el-input v-model="guestForm.email" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="submitGuestForm">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<style scoped>
.guests-page {
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

:deep(.guests-table) {
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

:deep(.guests-table .el-table__header-wrapper th) {
  background: #f8fafc;
  font-size: 14px;
  font-weight: 700;
}

:deep(.guests-table .el-table__body-wrapper td) {
  padding: 14px 0;
}

:deep(.action-btn .el-icon) {
  font-size: 20px;
}
</style>
