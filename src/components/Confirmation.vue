<template>
  <div class="content-wrapper">
    <div class="confirmation">
      <div class="check-icon">✓</div>
      <p>Thank you, your submission is being processed</p>
      <p class="grey">We will get back to shortly with the result of our decision.</p>
    </div>
    <div class="button-container">
      <button class="primary-button" @click="handleExit">
        Exit App
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'Confirmation',
  setup() {
    const handleExit = () => {
      const tg = (window as any).Telegram.WebApp;
      tg.close();
    };

    return { handleExit };
  }
})
</script>

<style>
.confirmation {
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  text-align: center;
}

.check-icon {
  width: 100px;
  height: 100px;
  background-color: rgba(69, 179, 105, 0.1);
  border: 1.5px solid #45B369;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 48px;
  color: #45B369;
}

.confirmation h2 {
  max-width: 80%;
  margin: 0 auto;
}
</style>
