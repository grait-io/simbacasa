<template>
  <div  class="content-wrapper">
    <div class="welcome">
      <div class="content">
        <img src="/logo.svg" alt="SimbiCasa Logo" class="logo centered-logo">
        <p>Welcome to <br>
        <b>SimbaCasa</b></p>
        <p class="grey">Feeling Home Community</p>
        <br/>
        <p>🏘🌍✨</p class="logo centered-logo">
      </div>
      <div class="button-container">
        <button @click="handleGetStarted" class="primary-button">
          Get started
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createPinia } from 'pinia'

export default defineComponent({
  name: 'Welcome',
  setup() {
    const router = useRouter()
    const tg = (window as any).Telegram.WebApp

    const handleGetStarted = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      try {
        tg.HapticFeedback?.impactOccurred?.('medium')
      } catch (e) {
        console.log('HapticFeedback not available')
      }
      router.push('/name')
    }

    onMounted(() => {
      try {
        tg.ready?.()
        tg.expand?.()
      } catch (e) {
        console.log('Telegram WebApp not fully available')
      }
    })

    return { handleGetStarted }
  }
})
</script>

<style>
.welcome {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 69vh;
  width: 100%;
  padding: 0;
  margin: 0;
  box-sizing: border-box;
  background-color: var(--background-color);
  overflow-x: hidden;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  width: 100%;
}

.logo {
  width: 200px;
  height: auto;
  max-width: 100%;
}

.centered-logo {
  display: block;
  margin-left: auto;
  margin-right: auto;
}

h1 {
  color: var(--text-color);
  margin-bottom: 8px;
}




</style>
