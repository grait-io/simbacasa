import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import Welcome from './components/Welcome.vue'
import Name from './components/Name.vue'
import Socials from './components/Socials.vue'
import AboutYou from './components/AboutYou.vue'
import Referrals from './components/Referrals.vue'
import Confirmation from './components/Confirmation.vue'
import tg from './telegram'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Welcome },
    { path: '/name', component: Name },
    { path: '/socials', component: Socials },
    { path: '/about-you', component: AboutYou },
    { path: '/referrals', component: Referrals },
    { path: '/confirmation', component: Confirmation },
  ]
})

const pinia = createPinia()

const app = createApp(App)

app.use(router)
app.use(pinia)

// Make Telegram WebApp instance available in all components
app.config.globalProperties.$tg = tg

// Mount the app
app.mount('#app')
