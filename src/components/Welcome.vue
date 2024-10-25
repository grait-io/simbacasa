<template>
  <div class="welcome">
    <img src="/logo.png" alt="SimbiCasa Logo" class="logo centered-logo">
    <h1>Welcome to SimbaCasa</h1>
    <p>Find, Offer and Swap Homes within a trusted Community</p>
    <button @click="handleGetStarted" class="primary-button">
      Get started
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'Welcome',
  setup() {
    const router = useRouter()
    const tg = (window as any).Telegram.WebApp

    const handleGetStarted = () => {
      tg.HapticFeedback.impactOccurred('medium')
      router.push('/name')
    }

    onMounted(() => {
      tg.ready()
      tg.expand()
    })

    return { handleGetStarted }
  }
})
</script>

<style scoped>
.welcome {
  /* Ensure centering by setting display to flex and justifying content */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  gap: 24px;
  text-align: center;
  padding: 16px;
  /* Add margin to ensure centering within parent container */
  margin: 0 auto;
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
  color: #2D5B62;
  margin-bottom: 8px;
}

p {
  color: #6B7280;
  margin-bottom: 24px;
}

/*.primary-button {
  width: 100%;
  max-width: 300px;
  padding: 12px 16px;
  background-color: #164951;
  color: #FFFFFF;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  cursor: pointer;
}*/
</style>
