import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import Welcome from './components/Welcome.vue'
import Name from './components/Name.vue'
import Socials from './components/Socials.vue'
import Questions from './components/Questions.vue'
import Referrals from './components/Referrals.vue'
import Photo from './components/Photo.vue'
import Confirmation from './components/Confirmation.vue'
import tg from './telegram'

// Create Pinia instance first
const pinia = createPinia()

// Create router after Pinia
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Welcome },
    { path: '/name', component: Name },
    { path: '/socials', component: Socials },
    { path: '/questions', component: Questions },
    { path: '/referrals', component: Referrals },
    { path: '/photo', component: Photo },
    { path: '/confirmation', component: Confirmation },
  ]
})

// Create app and use Pinia first
const app = createApp(App)
app.use(pinia)  // Install Pinia before router
app.use(router) // Then install router

// Make Telegram WebApp instance available in all components
app.config.globalProperties.$tg = tg

// Mount the app
app.mount('#app')
