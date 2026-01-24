import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import i18n from "./locales";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";

import "@/assets/styles/theme.css";
import "@/assets/styles/base.css";
import "@/assets/styles/components.css";

import { useAppStore } from "@/stores/app.store";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(i18n);
app.use(ElementPlus);

const appStore = useAppStore();
appStore.initTheme();
appStore.initLang();

app.mount("#app");
