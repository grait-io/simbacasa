<template>
  <div class="content-wrapper" @click="handleOutsideClick">
    <div class="referrals">
      <h2>Referrals</h2>
      <p class="title">How did you hear about us?</p>
      <p>Let us know if a friend referred you.</p>
      <input v-model="referralSource" type="text" placeholder="Referral Source">
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
    <div class="button-container">
      <button @click="handleSubmit" class="primary-button" :disabled="isSubmitting">
        {{ isSubmitting ? 'Submitting...' : 'Continue' }}
      </button>
      <button @click="handleBack" class="back-button">
        Back
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

export default defineComponent({
  name: 'Referrals',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()

    const referralSource = ref('')
    const error = ref('')
    const isSubmitting = ref(false)

    onMounted(() => {
      userStore.setTelegramUsername()
      console.log('Component mounted. Telegram username:', userStore.telegramUsername)
      console.log('Current user store state:', userStore.$state)
    })

    const handleSubmit = async () => {
      error.value = ''
      isSubmitting.value = true
      window.scrollTo({ top: 0, behavior: 'smooth' });
      userStore.updateUserData({ referralSource: referralSource.value })
      router.push('/photo')
      isSubmitting.value = false
    }

    const handleBack = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      router.back()
    }

    const handleOutsideClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('input')) {
        const activeElement = document.activeElement as HTMLElement
        activeElement?.blur?.()
      }
    }

    return { referralSource, handleSubmit, handleBack, error, isSubmitting, handleOutsideClick }
  }
})
</script>

<style>
.referrals {
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
