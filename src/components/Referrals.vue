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
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import tg from '../telegram'

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
    })

    const handleSubmit = async () => {
      error.value = ''
      isSubmitting.value = true
      window.scrollTo({ top: 0, behavior: 'smooth' });
      userStore.updateUserData({ referralSource: referralSource.value })
      
      try {
        console.log('User data before submission:', JSON.stringify(userStore.$state, null, 2))
        console.log('Submitting form with Telegram username:', userStore.telegramUsername)
        
        const url = new URL("https://teable.grait.io/api/table/tblmd41XoXrQFYtezww/record");
        
        // Use a temporary telegramID for testing in Chrome
        const tempTelegramID = 'temp_' + Math.random().toString(36).substr(2, 9)
        
        const telegramID = String(tg.initDataUnsafe?.user?.id || userStore.telegramUsername || tempTelegramID)
        console.log('TelegramID before submission:', telegramID, 'Type:', typeof telegramID)
        
        const payload = {
          records: [
            {
              fields: {
                "First name": String(userStore.$state.firstName),
                "Last Name": String(userStore.$state.lastName),
                "Instagram": String(userStore.$state.instagram),
                "About You": String(userStore.$state.about),
                "Referral Source": String(userStore.$state.referralSource),
                "status": "pending",
                "telegramID": telegramID
              }
            }
          ]
        }
        
        console.log('Payload being sent to API:', JSON.stringify(payload, null, 2))
        
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer teable_accwindRYobD2azy8ne_O83Or+XMAmIdRe4c5xEcWS7NDkYw9K20rF6O8+XqnbA=',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          const data = await response.json();
          console.log('Teable DB response:', data);
          router.push('/confirmation')
        } else {
          const errorText = await response.text();
          error.value = `Failed to save user data. Status: ${response.status}. Error: ${errorText}`;
          console.error('Teable DB error:', error.value);
        }
      } catch (err) {
        error.value = 'An error occurred. Please try again later. ' + (err instanceof Error ? err.message : String(err));
        console.error('Error:', err)
      } finally {
        isSubmitting.value = false
      }
    }

    const handleOutsideClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('input')) {
        const activeElement = document.activeElement as HTMLElement
        activeElement?.blur?.()
      }
    }

    return { referralSource, handleSubmit, error, isSubmitting, handleOutsideClick }
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
