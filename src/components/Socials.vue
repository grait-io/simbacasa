<template>
  <div class="content-wrapper" @click="handleOutsideClick">
    <div class="socials">
      <div class="header">
        <button @click="handleBack" class="back-button" aria-label="Go back">
          <span class="arrow">←</span>
          <span>go back</span>
        </button>
        <h2>Socials</h2>
      </div>
      
      <p class="grey">We require at least one social account in order to verify your identity securely.</p>
      <input v-model="instagram" type="text" placeholder="Instagram" @keydown.enter="focusLinkedin">
      <input v-model="linkedin" type="text" placeholder="LinkedIn" ref="linkedinInput">
    </div>
    <div class="button-container">
      <button @click="handleSubmit" class="primary-button" :disabled="!isFormValid">
        Continue
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

export default defineComponent({
  name: 'Socials',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()

    const instagram = ref('')
    const linkedin = ref('')
    const linkedinInput = ref<HTMLInputElement | null>(null)

    const isFormValid = computed(() => {
      return instagram.value.trim() !== '' || linkedin.value.trim() !== ''
    })

    const handleSubmit = () => {
      if (isFormValid.value) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        userStore.updateUserData({ instagram: instagram.value, linkedin: linkedin.value })
        router.push('/questions')
      }
    }

    const handleBack = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      router.back()
    }

    const focusLinkedin = () => {
      if (linkedinInput.value) {
        linkedinInput.value.focus()
      }
    }

    const handleOutsideClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('input')) {
        const activeElement = document.activeElement as HTMLElement
        activeElement?.blur?.()
      }
    }

    return { 
      instagram, 
      linkedin, 
      handleSubmit, 
      handleBack,
      linkedinInput, 
      focusLinkedin, 
      isFormValid, 
      handleOutsideClick 
    }
  }
})
</script>

<style>
.socials {
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  
}

.header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}


.page-title {
  font-size: 24px;
  color: var(--teal-700);
  margin: 0;
  padding: 0;
}
</style>
