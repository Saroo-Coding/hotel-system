<script setup>
/* ===================== CORE ===================== */
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

/* ===================== STORE ===================== */
import { useAuthStore } from "@/stores/auth.store";

/* ===================== COMPONENTS ===================== */
import ThemeToggle from "@/components/ThemeToggle.vue";
import LanguageToggle from "@/components/LanguageToggle.vue";

/* ===================== UI LIB ===================== */
import { ElMessage } from "element-plus";

/* ===================== ASSETS ===================== */
import loginAdminImg from "@/assets/images/login_admin.jpg";

/* ===================== SETUP ===================== */
const { t } = useI18n();
const router = useRouter();
const authStore = useAuthStore();

/* ===================== STATE ===================== */
const username = ref("");
const password = ref("");
const activeTab = ref("email");
const rememberMe = ref(false);
const loading = ref(false);

/* ===================== METHODS ===================== */
const submit = async () => {
  if (!username.value || !password.value) return;

  loading.value = true;
  try {
    await authStore.login(username.value, password.value);
    router.push("/");
  } catch (err) {
    ElMessage.error(err?.message || t("login.error"));
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="login-container">
    <!-- LEFT IMAGE -->
    <div class="login-image">
      <img :src="loginAdminImg" alt="Hotel" />
      <div class="image-overlay">
        <div class="image-text">
          <h2>{{ t("login.sologan_1") }}</h2>
          <p>{{ t("login.sologan_2") }}</p>
        </div>
      </div>
    </div>

    <!-- RIGHT FORM -->
    <div class="login-right">
      <div class="top-actions">
        <ThemeToggle />
        <LanguageToggle />
      </div>

      <div class="form-wrapper">
        <div class="form-content">
          <h2>{{ t("login.title") }}</h2>

          <el-form @submit.prevent="submit">
            <el-tabs v-model="activeTab">
              <el-tab-pane :label="t('login.email')" name="email">
                <el-form-item>
                  <label>{{ t("login.email") }}</label>
                  <el-input
                    v-model="username"
                    type="email"
                    :placeholder="t('login.placeholder_email')"
                    size="large"
                    clearable
                  />
                </el-form-item>
              </el-tab-pane>

              <el-tab-pane :label="t('login.phone')" name="phone">
                <el-form-item>
                  <label>{{ t("login.phone") }}</label>
                  <el-input
                    v-model="username"
                    type="text"
                    :placeholder="t('login.placeholder_phone')"
                    size="large"
                    clearable
                  />
                </el-form-item>
              </el-tab-pane>
            </el-tabs>

            <el-form-item>
              <label>{{ t("login.password") }}</label>
              <el-input
                v-model="password"
                type="password"
                :placeholder="t('login.placeholder_pass')"
                size="large"
                show-password
              />
            </el-form-item>

            <div class="form-row">
              <el-checkbox v-model="rememberMe">
                {{ t("login.remember") }}
              </el-checkbox>
              <a class="forgot">{{ t("login.forgot_pass") }}</a>
            </div>

            <el-button
              class="login-btn"
              type="primary"
              size="large"
              :loading="loading"
              @click="submit"
            >
              {{ t("common.login") }}
            </el-button>
          </el-form>

          <el-divider>{{ t("login.or_login") }}</el-divider>

          <div class="social-login">
            <el-button class="google-btn" plain>
              <img
                src="https://www.svgrepo.com/show/475656/google-color.svg"
                width="20"
                style="margin-right: 8px"
              />
              Google
            </el-button>
            <el-button class="facebook-btn" plain>
              <img
                src="https://www.svgrepo.com//show/448224/facebook.svg"
                width="20"
                style="margin-right: 8px"
              />
              Facebook
            </el-button>
          </div>

          <div class="register-link">
            {{ t("login.no_account") }}
            <a>{{ t("common.register") }}</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
}
.login-image {
  flex: 1.2;
  position: relative;
  display: flex;
  align-items: stretch;
  min-width: 0;
}
.login-image img {
  width: 100%;
  height: 100vh;
  object-fit: cover;
}
.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.25);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 32px;
}
.image-text {
  margin-top: auto;
}
.image-text h2 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}
.image-text p {
  font-size: 1.1rem;
}
.login-form {
  flex: 1.5;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.form-content {
  width: 100%;
  max-width: 500px;
  background: #fff;
  border-radius: 16px;
  padding: 25px 30px;
  box-shadow: 0 4px 32px rgba(0, 0, 0, 0.08);
  position: relative;
  color: #000000;
}

.form-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
  font-size: 0.98rem;
}
.forgot {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.98rem;
}
.login-btn {
  width: 100%;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 8px;
}
.social-login {
  display: flex;
  gap: 12px;
  margin-bottom: 18px;
}
.google-btn,
.facebook-btn {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fafafa;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 8px 0;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.google-btn:hover,
.facebook-btn:hover {
  background: #f1f1f1;
}
.register-link {
  text-align: center;
  color: #888;
  font-size: 1rem;
}
.register-link a {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.login-right {
  flex: 1.5;
}

.top-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin: 8px 12px;
}

.form-wrapper {
  height: 90vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.form-content {
  max-width: 500px;
  width: 100%;
  padding: 25px 30px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 4px 32px rgba(0, 0, 0, 0.08);
}
</style>
