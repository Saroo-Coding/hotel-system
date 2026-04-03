<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { changeAdminUserStatus, createAdminUser, getAdminUserDetail, listAdminUsers, updateAdminUser } from '@/api/dashboard.api';
import { Plus, Edit, Lock, Unlock, Refresh } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useAuthStore } from '@/stores/auth.store';

const { t } = useI18n();
const authStore = useAuthStore();

const users = ref([]);
const loading = ref(false);
const submitting = ref(false);
const keyword = ref('');

const dialogVisible = ref(false);
const dialogMode = ref('create');
const formRef = ref(null);

const canManageUsers = computed(() => authStore.user?.role === 'ADMIN');

const defaultForm = () => ({
  id: '',
  email: '',
  phone: '',
  full_name: '',
  role: 'STAFF',
  status: 'ACTIVE',
});

const userForm = reactive(defaultForm());

const formRules = computed(() => ({
  full_name: [{ required: true, message: t('users.fullName') + ' ' + t('common.required'), trigger: 'blur' }],
}));

const normalizeStatus = (status) => {
  if (!status) return 'INACTIVE';
  if (typeof status === 'string') {
    if (status.includes('.')) return status.split('.').pop();
    return status;
  }
  if (typeof status === 'object' && status.value) return status.value;
  return 'INACTIVE';
};

const getErrorMessage = (error, fallbackKey = 'common.internal_server_error') => {
  if (typeof error?.detail === 'string') return t(error.detail);
  if (error?.detail && typeof error.detail === 'object') {
    const firstField = Object.values(error.detail)[0];
    if (typeof firstField === 'string') return t(firstField);
  }
  return t(fallbackKey);
};

const fetchUsers = async () => {
  loading.value = true;
  try {
    const response = await listAdminUsers({
      page: 1,
      limit: 100,
      role: 'STAFF',
      keyword: keyword.value,
    });
    users.value = (response.data || []).map((item) => ({
      ...item,
      status: normalizeStatus(item.status),
    }));
  } catch (error) {
    ElMessage.error(getErrorMessage(error));
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  Object.assign(userForm, defaultForm());
};

const openCreateDialog = () => {
  if (!canManageUsers.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }
  dialogMode.value = 'create';
  resetForm();
  dialogVisible.value = true;
};

const openEditDialog = async (user) => {
  if (!canManageUsers.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }
  dialogMode.value = 'edit';
  try {
    loading.value = true;
    const response = await getAdminUserDetail(user.id);
    const detail = response.data || {};
    Object.assign(userForm, {
      id: detail.id,
      email: detail.email || '',
      phone: detail.phone || '',
      full_name: detail.full_name || '',
      role: detail.role || 'STAFF',
      status: normalizeStatus(detail.status),
    });
    dialogVisible.value = true;
  } catch (error) {
    ElMessage.error(getErrorMessage(error));
  } finally {
    loading.value = false;
  }
};

const submitUserForm = async () => {
  if (!canManageUsers.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }

  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitting.value = true;
  try {
    if (dialogMode.value === 'create') {
      const payload = {
        email: userForm.email?.trim() || null,
        phone: userForm.phone?.trim() || null,
        full_name: userForm.full_name?.trim(),
        role: 'STAFF',
      };
      await createAdminUser(payload);
      ElMessage.success(t('users.created'));
    } else {
      const payload = {
        full_name: userForm.full_name?.trim(),
        role: userForm.role,
        status: userForm.status,
      };
      await updateAdminUser(userForm.id, payload);
      ElMessage.success(t('users.updated'));
    }

    dialogVisible.value = false;
    resetForm();
    await fetchUsers();
  } catch (error) {
    ElMessage.error(getErrorMessage(error));
  } finally {
    submitting.value = false;
  }
};

const handleToggleStatus = async (user) => {
  if (!canManageUsers.value) {
    ElMessage.warning(t('error.FORBIDDEN'));
    return;
  }
  const nextStatus = user.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
  const confirmMessage = user.status === 'ACTIVE' ? t('users.confirmLock') : t('users.confirmUnlock');

  try {
    await ElMessageBox.confirm(confirmMessage, t('common.warning'), {
      confirmButtonText: t('common.ok'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    });

    loading.value = true;
    await changeAdminUserStatus(user.id, nextStatus);
    ElMessage.success(nextStatus === 'ACTIVE' ? t('users.unlocked') : t('users.locked'));
    await fetchUsers();
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(getErrorMessage(error));
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchUsers();
});
</script>

<template>
  <AdminLayout>
    <div class="users-page">
      <div class="page-header">
        <h1>{{ t('admin.staffs') }}</h1>
        <div class="actions">
          <el-input v-model="keyword" clearable :placeholder="t('dashboard.search')" style="width: 220px" @keyup.enter="fetchUsers" />
          <el-button :icon="Refresh" @click="fetchUsers">{{ t('rooms.refresh') }}</el-button>
          <el-button v-if="canManageUsers" type="primary" :icon="Plus" @click="openCreateDialog">
            {{ t('common.addNew') }}
          </el-button>
        </div>
      </div>

      <el-table :data="users" stripe border class="users-table" v-loading="loading">
        <el-table-column prop="email" :label="t('users.email')" min-width="200" />
        <el-table-column prop="full_name" :label="t('users.fullName')" min-width="180" />
        <el-table-column prop="phone" :label="t('users.phone')" width="140" />
        <el-table-column prop="role" :label="t('users.role')" width="120" align="center">
          <template #default="{ row }">
            <el-tag effect="plain">{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('users.status')" width="130" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'danger'" effect="plain">
              {{ row.status === 'ACTIVE' ? t('users.active') : t('users.inactive') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="canManageUsers" :label="t('common.actions')" width="170" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="large" class="action-btn" type="primary" :icon="Edit" @click="openEditDialog(row)" text />
            <el-button
              v-if="row.status === 'ACTIVE'"
              size="large"
              class="action-btn"
              type="warning"
              :icon="Lock"
              @click="handleToggleStatus(row)"
              text
            />
            <el-button
              v-else
              size="large"
              class="action-btn"
              type="success"
              :icon="Unlock"
              @click="handleToggleStatus(row)"
              text
            />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? t('users.createStaff') : t('users.editStaff')"
      width="620px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="userForm" :rules="formRules" label-position="top">
        <el-form-item :label="t('users.fullName')" prop="full_name">
          <el-input v-model="userForm.full_name" />
        </el-form-item>
        <el-form-item :label="t('users.email')">
          <el-input v-model="userForm.email" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item :label="t('users.phone')">
          <el-input v-model="userForm.phone" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item :label="t('users.role')" v-if="dialogMode === 'edit'">
          <el-select v-model="userForm.role">
            <el-option label="STAFF" value="STAFF" />
            <el-option label="CUSTOMER" value="CUSTOMER" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('users.status')" v-if="dialogMode === 'edit'">
          <el-select v-model="userForm.status">
            <el-option label="ACTIVE" value="ACTIVE" />
            <el-option label="INACTIVE" value="INACTIVE" />
            <el-option label="BANNED" value="BANNED" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="submitUserForm">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<style scoped>
.users-page {
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

:deep(.users-table) {
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

:deep(.users-table .el-table__header-wrapper th) {
  background: #f8fafc;
  font-size: 14px;
  font-weight: 700;
}

:deep(.users-table .el-table__body-wrapper td) {
  padding: 14px 0;
}

:deep(.action-btn .el-icon) {
  font-size: 20px;
}
</style>
