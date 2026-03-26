<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import { InfoFilled } from "@element-plus/icons-vue";

import { useAppStore } from "@/stores/app.store";

import bgLight from "@/assets/images/register_light_mode.webp";
import bgDark from "@/assets/images/register_dark_mode.webp";

import ThemeToggle from "@/components/ThemeToggle.vue";
import LanguageToggle from "@/components/LanguageToggle.vue";

const { t } = useI18n();
const router = useRouter();
const appStore = useAppStore();

/* ===================== STATE ===================== */
const form = ref({
  email: "",
  phone: "",
  full_name: "",
  password: "",
  confirmPassword: "",
});

const loading = ref(false);

/* ===================== COMPUTED ===================== */
const backgroundImage = computed(() =>
  appStore.theme === "dark" ? bgDark : bgLight,
);

/* ===================== METHODS ===================== */
const submit = async () => {
  // if (form.value.password !== form.value.confirmPassword) {
  //   ElMessage.error(t('register.password_not_match'))
  //   return
  // }
  // loading.value = true
  // try {
  //   // TODO: call register API
  //   ElMessage.success(t('register.success'))
  //   router.push('/login')
  // } catch (err) {
  //   ElMessage.error(err?.message || t('register.error'))
  // } finally {
  //   loading.value = false
  // }
};
</script>

<template>
  <div
    class="register-page"
    :style="{ backgroundImage: `url(${backgroundImage})` }"
  >
    <div class="overlay"></div>

    <div class="top-actions">
      <ThemeToggle />
      <LanguageToggle />
    </div>

    <div class="form-wrapper">
      <el-card class="register-card">
        <h2 class="title">{{ t("auth.title_register") }}</h2>

        <el-form @submit.prevent="submit">
          <el-form-item :label="t('auth.email')" label-position="top">
            <el-input
              v-model="form.email"
              type="email"
              size="large"
              :placeholder="t('auth.placeholder_email')"
              clearable
            />
          </el-form-item>

          <el-form-item>
            <el-tooltip :content="t('auth.phone_tooltip')" placement="right" effect="light">
              <label>{{ t("auth.phone") }} <el-icon color="#909399"><InfoFilled /></el-icon></label>
            </el-tooltip>
            <el-input
              v-model="form.phone"
              size="large"
              :placeholder="t('auth.placeholder_phone')"
              clearable
            />
          </el-form-item>

          <el-form-item :label="t('auth.full_name')" label-position="top">
            <el-input
              v-model="form.full_name"
              size="large"
              :placeholder="t('auth.placeholder_full_name')"
              clearable
            />
          </el-form-item>

          <el-form-item :label="t('auth.password')" label-position="top">
            <el-input
              v-model="form.password"
              type="password"
              size="large"
              :placeholder="t('auth.placeholder_pass')"
              show-password
            />
          </el-form-item>

          <el-form-item
            :label="t('auth.confirm_password')"
            label-position="top"
          >
            <el-input
              v-model="form.confirmPassword"
              type="password"
              size="large"
              :placeholder="t('auth.placeholder_confirm_pass')"
              show-password
            />
          </el-form-item>

          <el-button
            class="login-btn"
            type="primary"
            size="large"
            :loading="loading"
            @click="submit"
          >
            <span v-if="!loading">{{ t("common.register") }}</span>
          </el-button>
        </el-form>

        <div class="login-link">
          {{ t("auth.have_account") }}
          <a @click.prevent="router.push('/login')">
            {{ t("common.login") }}
          </a>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  height: 100vh;
  background-size: cover;
  background-position: center;
  position: relative;
}

.overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
}

.top-actions {
  position: relative;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 8px 12px;
}

.form-wrapper {
  position: relative;
  z-index: 1;
  /* height: 100%; */
  display: flex;
  justify-content: center;
  align-items: center;
}

.register-card {
  width: 100%;
  max-width: 500px;
  padding: 10px;
  border-radius: 16px;
}

.title {
  text-align: center;
  margin: 10px;
}

.login-link {
  margin-top: 10px;
  text-align: center;
  color: #888;
  font-size: 1rem;
}

.login-link a {
  color: #3b82f6;
  cursor: pointer;
  font-weight: 500;
}

.login-btn {
  width: 100%;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 8px;
}
</style>
