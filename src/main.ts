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

// Create Pinia instance first
const pinia = createPinia()

// Create router after Pinia
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Welcome },
    { 
      path: '/name', 
      component: Name,
      beforeEnter: (to, from, next) => {
        // Ensure Pinia is initialized before entering the route
        try {
          const app = createApp({})
          app.use(pinia)
          next()
        } catch (e) {
          console.error('Failed to initialize Pinia:', e)
          next(false)
        }
      }
    },
    { path: '/socials', component: Socials },
    { path: '/about-you', component: AboutYou },
    { path: '/referrals', component: Referrals },
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
