<template>
  <div class="content-wrapper" @click="handleOutsideClick">
    <div class="name">
      
      <h2>📝 Your Details</h2>
      <p class="grey">Find, offer and swap homes with a trusted community. </p>
      <input 
        v-model="firstName" 
        type="text" 
        placeholder="First Name" 
        @keydown.enter="focusLastName"
        @focus="handleInputFocus"
      >
      <input 
        v-model="lastName" 
        type="text" 
        placeholder="Last Name" 
        ref="lastNameInput" 
        @keydown.enter="handleSubmit"
        @focus="handleInputFocus"
      >
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
    const store = useStore() // Now properly calling the function

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

    const handleInputFocus = (event: FocusEvent) => {
      const target = event.target as HTMLElement
      setTimeout(() => {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 300)
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
      handleOutsideClick,
      handleInputFocus
    }
  }
})
</script>

<style>
.name {
  padding-top: 20px;
  display: flex;
  flex-direction: column;
}

.name input {
  margin-top: 8px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  font-size: 16px; /* Prevents iOS zoom on focus */
}

@supports (-webkit-touch-callout: none) {
  .content-wrapper {
    /* iOS-specific fix */
    padding-bottom: max(env(safe-area-inset-bottom), 20px);
  }
}
</style>
