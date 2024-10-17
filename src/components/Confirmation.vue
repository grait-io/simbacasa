<template>
  <div class="content-wrapper">
    <div class="confirmation">
      <div class="check-icon">✓</div>
      <h2>Thank you, your application is being processed</h2>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'Confirmation'
})
</script>

<style scoped>
.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding: 16px;
  gap: 16px;
}

.confirmation {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  gap: 24px;
  text-align: center;
}

.check-icon {
  width: 100px;
  height: 100px;
  background-color: #ECF7F0;
  border: 1.5px solid #45B369;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 48px;
  color: #45B369;
}

h2 {
  max-width: 80%;
  margin: 0 auto;
}

.primary-button {
  width: 100%;
  padding: 8px 16px;
  background-color: #164951;
  color: #FFFFFF;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  cursor: pointer;
}
</style>
