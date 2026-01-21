import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

createApp(App)
  .use(createPinia())
  .use(router)
  .mount('#app')

// import { i18n } from './i18n'
// import { useAppStore } from '@/stores/app.store'

// const app = createApp(App)

// app.use(createPinia())
// app.use(i18n)
// app.use(router)
// app.mount('#app')

// // init app settings
// const appStore = useAppStore()
// appStore.initTheme()
// appStore.initLanguage(i18n)
