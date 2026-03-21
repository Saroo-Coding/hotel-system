<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
const currentYear = computed(() => new Date().getFullYear());

const mapEmbedSrc =
  "https://www.google.com/maps?q=10.7769,106.7009&z=14&output=embed";
</script>

<template>
  <footer class="dashboard-footer">
    <div class="footer-inner">
      <div class="footer-grid">
        <section class="footer-col">
          <h3>{{ t("dashboard.logo") }}</h3>
          <p>{{ t("dashboard.footerTagline") }}</p>
          <p>{{ t("dashboard.footerAddress") }}</p>
          <p>{{ t("dashboard.footerPhone") }}</p>
          <p>{{ t("dashboard.footerEmail") }}</p>
        </section>

        <section class="footer-col">
          <h4>{{ t("dashboard.footerQuickLinks") }}</h4>
          <a href="#">{{ t("dashboard.home") }}</a>
          <a href="#rooms">{{ t("dashboard.room") }}</a>
          <a href="#">{{ t("dashboard.search") }}</a>

          <h4 class="hours-title">{{ t("dashboard.footerHoursTitle") }}</h4>
          <p>{{ t("dashboard.footerHoursValue") }}</p>
        </section>

        <section class="footer-col map-col">
          <h4>{{ t("dashboard.footerMapTitle") }}</h4>
          <div class="map-frame">
            <iframe
              :src="mapEmbedSrc"
              width="100%"
              height="220"
              style="border: 0"
              allowfullscreen=""
              loading="lazy"
              referrerpolicy="no-referrer-when-downgrade"
              :title="t('dashboard.footerMapTitle')"
            ></iframe>
          </div>
        </section>
      </div>
    </div>

    <div class="footer-bottom">
      <div class="footer-bottom-inner">
        <span>(C) {{ currentYear }} {{ t("dashboard.logo") }}</span>
        <span>{{ t("dashboard.footerRights") }}</span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.dashboard-footer {
  margin-top: 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.footer-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 24px 16px 10px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.9fr 1.6fr;
  gap: 20px;
}

.footer-col h3,
.footer-col h4 {
  margin: 0 0 10px;
  color: var(--text-primary);
}

.footer-col p {
  margin: 0 0 8px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.footer-col a {
  display: block;
  margin-bottom: 8px;
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
}

.footer-col a:hover {
  text-decoration: underline;
}

.hours-title {
  margin-top: 14px;
}

.map-col {
  min-width: 0;
}

.map-frame {
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.footer-bottom {
  border-top: 1px solid var(--border-color);
  margin-top: 16px;
}

.footer-bottom-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 12px 16px;
  color: var(--text-secondary);
  font-size: 13px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

@media (max-width: 980px) {
  .footer-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .footer-bottom-inner {
    flex-direction: column;
  }
}
</style>

