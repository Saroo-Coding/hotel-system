import { defineStore } from "pinia";
import i18n from "@/locales";

export const useAppStore = defineStore("app", {
  state: () => ({
    theme: localStorage.getItem("theme") || "light",

    lang: localStorage.getItem("lang") || "vi"
  }),

  actions: {
    initTheme() {
      document.documentElement.setAttribute("data-theme", this.theme);
    },

    toggleTheme() {
      this.theme = this.theme === "light" ? "dark" : "light";
      localStorage.setItem("theme", this.theme);
      document.documentElement.setAttribute("data-theme", this.theme);
    },

    setTheme(theme) {
      this.theme = theme;
      localStorage.setItem("theme", theme);
      document.documentElement.setAttribute("data-theme", theme);
    },

    initLang() {
      i18n.global.locale.value = this.lang;
    },

    toggleLang() {
      this.lang = this.lang === "vi" ? "en" : "vi";
      localStorage.setItem("lang", this.lang);
      i18n.global.locale.value = this.lang;
    },

    setLang(lang) {
      this.lang = lang;
      localStorage.setItem("lang", lang);
      i18n.global.locale.value = lang;
    }
  }
});
