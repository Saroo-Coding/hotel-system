<script setup>
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";

const router = useRouter();
const { t } = useI18n();
const tr = (key, fallback) => {
  const value = t(key);
  return value === key ? fallback : value;
};
</script>

<template>
  <div class="not-found-page">
    <Header />

    <main class="not-found-container">
      <div class="theme-orb theme-orb-left" />
      <div class="theme-orb theme-orb-right" />

      <section class="not-found-card">
        <p class="code">404</p>
        <h1>{{ tr("notFound.title", "Page Not Found") }}</h1>
        <p class="description">
          {{ tr("notFound.description", "The page or room you are looking for does not exist or may have been removed.") }}
        </p>

        <div class="actions">
          <el-button class="primary-btn" type="primary" size="large" @click="router.push('/')">
            {{ tr("notFound.goHome", "Back to Home") }}
          </el-button>
          <el-button class="secondary-btn" size="large" @click="router.back()">
            {{ t("common.returnBack") }}
          </el-button>
        </div>
      </section>
    </main>

    <Footer />
  </div>
</template>

<style scoped>
.not-found-page {
  min-height: 100vh;
  background: var(--page-gradient);
}

.not-found-container {
  position: relative;
  max-width: 1120px;
  margin: 0 auto;
  padding: 40px 16px 56px;
}

.not-found-card {
  position: relative;
  z-index: 1;
  margin: 22px auto 0;
  max-width: 760px;
  padding: clamp(28px, 5vw, 54px);
  border-radius: 30px;
  border: 1px solid var(--border-color);
  background: var(--hero-surface);
  box-shadow: var(--shadow-strong);
  text-align: center;
}

.code {
  margin: 0;
  font-size: clamp(72px, 16vw, 140px);
  line-height: 0.9;
  font-weight: 800;
  color: var(--primary);
  letter-spacing: 0.03em;
}

h1 {
  margin: 18px 0 10px;
  font-size: clamp(26px, 4vw, 42px);
  color: var(--text-primary);
}

.description {
  margin: 0 auto;
  max-width: 520px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 26px;
  flex-wrap: wrap;
}

.primary-btn {
  border: none;
  border-radius: 14px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  box-shadow: 0 14px 24px color-mix(in srgb, var(--primary) 26%, transparent);
}

.secondary-btn {
  border-radius: 14px;
  font-weight: 600;
}

.theme-orb {
  position: absolute;
  border-radius: 999px;
  pointer-events: none;
  filter: blur(8px);
  opacity: 0.55;
}

.theme-orb-left {
  top: 110px;
  left: -26px;
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

@media (max-width: 576px) {
  .actions :deep(.el-button) {
    width: 100%;
  }
}
</style>
