<template>
  <div class="content-wrapper" @click="handleOutsideClick">
    <div class="socials">
      <h2>Socials</h2>
      <p class="title">Add your social accounts</p>
      <p>We require at least one social account in order to verify your identity securely.</p>
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
        userStore.updateUserData({ instagram: instagram.value, linkedin: linkedin.value })
        router.push('/about-you')
      }
    }

    const focusLinkedin = () => {
      if (linkedinInput.value) {
        linkedinInput.value.focus()
      }
    }

    const handleOutsideClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('input')) {
        document.activeElement?.blur()
      }
    }

    return { instagram, linkedin, handleSubmit, linkedinInput, focusLinkedin, isFormValid, handleOutsideClick }
  }
})
</script>

