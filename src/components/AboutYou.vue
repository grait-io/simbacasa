<template>
  <div class="content-wrapper" @click="handleOutsideClick">
    <div class="about-you">
      <h2>About You</h2>
      <p class="title">Share a little about yourself</p>
      <p>Write up to 200 words to let us and other users understand who you are.</p>
      <textarea v-model="about" placeholder="About you" maxlength="200" ref="aboutTextarea"></textarea>
    </div>
    <div class="button-container">
      <button @click="handleSubmit" class="primary-button">
        Continue
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

export default defineComponent({
  name: 'AboutYou',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()

    const about = ref('')
    const aboutTextarea = ref<HTMLTextAreaElement | null>(null)

    const handleSubmit = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      userStore.updateUserData({ about: about.value })
      router.push('/referrals')
    }

    const handleOutsideClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('textarea')) {
        const activeElement = document.activeElement as HTMLElement
        activeElement?.blur?.()
      }
    }

    return { about, handleSubmit, aboutTextarea, handleOutsideClick }
  }
})
</script>

<style>
.about-you {
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
