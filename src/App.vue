<template>
  <div id="app" :class="{ 'dark-theme': isDarkTheme }">
    <img v-if="!isWelcomePage" src="/logo.png" alt="Logo" class="app-logo" />
    <router-view></router-view>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserStore } from './store/user'
import { useRoute } from 'vue-router'
import './style.css'  // Import the centralized styles

export default defineComponent({
  name: 'App',
  setup() {
    const isDarkTheme = ref(false)
    let userStore: ReturnType<typeof useUserStore> | null = null
    const telegramUsername = ref('')
    const route = useRoute()

    const isWelcomePage = computed(() => {
      return route.path === '/' || route.path === '/welcome'
    })

    onMounted(() => {
      // Initialize store after component is mounted
      userStore = useUserStore()
      
      // Ensure Telegram WebApp is available
      if (window.Telegram?.WebApp) {
        const tg = window.Telegram.WebApp
        
        // Set the header color
        tg.setHeaderColor?.(tg.headerColor)

        // Set the background color
        tg.setBackgroundColor?.(tg.backgroundColor)

        // Check if dark theme is enabled
        isDarkTheme.value = tg.colorScheme === 'dark'

        // Listen for theme changes
        tg.onEvent?.('themeChanged', () => {
          isDarkTheme.value = tg.colorScheme === 'dark'
        })

        // Set Telegram username only if store is initialized
        if (userStore) {
          userStore.setTelegramUsername()
          telegramUsername.value = userStore.telegramUsername
        }
      } else {
        console.log('Telegram WebApp not available')
      }
    })

    return {
      isDarkTheme,
      telegramUsername,
      isWelcomePage
    }
  }
})
</script>

<style>
.app-logo {
  width: 33%;
  display: block;
  margin: 0 auto;
  padding: 10px 0;
}

.logo {
  width: 100px;
  height: 100px;
  margin-bottom: 20px;
}

.check-icon {
  width: 100px;
  height: 100px;
  background-color: var(--tg-theme-secondary-bg-color, #f0f0f0);
  border: 1.5px solid var(--tg-theme-button-color, #3390ec);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 48px;
  color: var(--tg-theme-button-color, #3390ec);
  margin: 0 auto 20px;
}
</style>
