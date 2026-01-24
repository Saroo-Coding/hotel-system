import { createI18n } from "vue-i18n";
import en from "./en.json";
import vi from "./vi.json";

const locale = localStorage.getItem("lang") || "vi";

const i18n = createI18n({
  legacy: false,
  locale,
  fallbackLocale: "en",
  messages: {
    en,
    vi
  }
});

export default i18n;
