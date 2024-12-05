<template>
  <div class="content-wrapper" @click="handleOutsideClick">
    <div class="socials">
      <div class="header">
        <button @click="handleBack" class="back-button" aria-label="Go back">
          <span class="arrow">←</span>
          <span>go back</span>
        </button>
        <h2>🌐 Socials</h2>
      </div>
      
      <p class="grey">We require at least one social account in order to verify your identity securely.</p>
      <div class="input-group">
        <span class="prefix">https://www.instagram.com/</span>
        <input v-model="instagram" type="text" placeholder="username" @keydown.enter="focusLinkedin">
      </div>
      <div class="input-group">
        <span class="prefix">linkedin.com/in/</span>
        <input v-model="linkedin" type="text" placeholder="username" ref="linkedinInput">
      </div>
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

    const normalizeLinks = () => {
      let normalizedInstagram = instagram.value.trim()
      let normalizedLinkedin = linkedin.value.trim()

      // Normalize Instagram
      if (normalizedInstagram) {
        normalizedInstagram = normalizedInstagram.replace('https://www.instagram.com/', '')
        normalizedInstagram = normalizedInstagram.replace('www.instagram.com/', '')
        normalizedInstagram = normalizedInstagram.replace('@', '')
        normalizedInstagram = `https://www.instagram.com/${normalizedInstagram}`
      }

      // Normalize LinkedIn
      if (normalizedLinkedin) {
        normalizedLinkedin = normalizedLinkedin.replace('https://www.linkedin.com/in/', '')
        normalizedLinkedin = normalizedLinkedin.replace('www.linkedin.com/in/', '')
        normalizedLinkedin = normalizedLinkedin.replace('linkedin.com/in/', '')
        normalizedLinkedin = `https://www.linkedin.com/in/${normalizedLinkedin}`
      }

      return { normalizedInstagram, normalizedLinkedin }
    }

    const handleSubmit = () => {
      if (isFormValid.value) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        const { normalizedInstagram, normalizedLinkedin } = normalizeLinks()
        userStore.updateUserData({ 
          instagram: normalizedInstagram, 
          linkedin: normalizedLinkedin 
        })
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
  gap: 16px;
}

.header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.input-group .prefix {
  padding: 8px 0 8px 12px;
  color: #666;
  font-size: 14px;
  white-space: nowrap;
}

.input-group input {
  border: none;
  padding: 8px;
  flex: 1;
  min-width: 0;
}

.input-group input:focus {
  outline: none;
}

.page-title {
  font-size: 24px;
  color: var(--teal-700);
  margin: 0;
  padding: 0;
}
</style>
