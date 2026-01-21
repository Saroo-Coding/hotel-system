import { defineStore } from 'pinia'

const THEME_KEY = 'app_theme'
const LANG_KEY = 'app_lang'

export const useAppStore = defineStore('app', {
  state: () => ({
    theme: 'light',   // 'light' | 'dark'
    language: 'vi'    // 'vi' | 'en'
  }),

  getters: {
    isDark: (state) => state.theme === 'dark'
  },

  actions: {

    initTheme() {
      const savedTheme = localStorage.getItem(THEME_KEY)

      if (savedTheme) {
        this.setTheme(savedTheme)
        return
      }

      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      this.setTheme(prefersDark ? 'dark' : 'light')
    },

    setTheme(theme) {
      if (!['light', 'dark'].includes(theme)) return

      this.theme = theme
      localStorage.setItem(THEME_KEY, theme)

      document.documentElement.setAttribute('data-theme', theme)
    },

    toggleTheme() {
      const nextTheme = this.theme === 'light' ? 'dark' : 'light'
      this.setTheme(nextTheme)
    },


    initLanguage(i18n) {
      const savedLang = localStorage.getItem(LANG_KEY)

      if (savedLang) {
        this.setLanguage(savedLang, i18n)
        return
      }

      const browserLang = navigator.language.startsWith('en') ? 'en' : 'vi'
      this.setLanguage(browserLang, i18n)
    },

    setLanguage(lang, i18n) {
      if (!['vi', 'en'].includes(lang)) return

      this.language = lang
      localStorage.setItem(LANG_KEY, lang)

      if (i18n) {
        i18n.global.locale.value = lang
      }
    }
  }
})
