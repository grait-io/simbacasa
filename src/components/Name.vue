<template>
  <div class="content-wrapper" @click="handleOutsideClick">
    <div class="name">
      <h2>Your details</h2>
      <p class="title">Find, offer and swap homes with a trusted community</p>
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
import { useUserStore } from '../store/user'

export default defineComponent({
  name: 'Name',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const tg = (window as any).Telegram.WebApp

    const firstName = ref('')
    const lastName = ref('')
    const lastNameInput = ref<HTMLInputElement | null>(null)

    const isFormValid = computed(() => firstName.value.trim() && lastName.value.trim())

    const handleSubmit = () => {
      if (isFormValid.value) {
        userStore.updateUserData({ firstName: firstName.value, lastName: lastName.value })
        tg.HapticFeedback.impactOccurred('medium')
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
        document.activeElement?.blur()
      }
    }

    onMounted(() => {
      tg.ready()
      tg.expand()
    })

    return { firstName, lastName, handleSubmit, isFormValid, lastNameInput, focusLastName, handleOutsideClick }
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
