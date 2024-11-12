<template>
  <div class="content-wrapper" @click="handleOutsideClick">
    <div class="name">
      <p>Your Details</p>
      <p class="grey">Find, offer and swap homes with a trusted community</p>
      <input v-model="firstName" type="text" placeholder="First Name" @keydown.enter="focusLastName">
      <input v-model="lastName" type="text" placeholder="Last Name" ref="lastNameInput" @keydown.enter="handleSubmit">
    </div>
    <div class="button-container">
      <button @click="handleSubmit" class="primary-button" :disabled="!isFormValid">
        Continue
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '../composables/useStore'

export default defineComponent({
  name: 'Name',
  setup() {
    const router = useRouter()
    const firstName = ref('')
    const lastName = ref('')
    const lastNameInput = ref<HTMLInputElement | null>(null)
    const store = useStore()

    const isFormValid = computed(() => firstName.value.trim() && lastName.value.trim())

    const handleSubmit = () => {
      if (isFormValid.value) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        store.updateUserData({ firstName: firstName.value, lastName: lastName.value })
        try {
          const tg = (window as any).Telegram?.WebApp
          tg?.HapticFeedback?.impactOccurred?.('medium')
        } catch (e) {
          console.log('HapticFeedback not available')
        }
        router.push('/socials')
      }
    }

    const focusLastName = () => {
      if (lastNameInput.value) {
        lastNameInput.value.focus()
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
      firstName, 
      lastName, 
      handleSubmit, 
      isFormValid, 
      lastNameInput, 
      focusLastName, 
      handleOutsideClick 
    }
  }
})
</script>

<style>
.name {
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
