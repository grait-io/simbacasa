import { ref } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import { useUserStore } from '../store/user'

const pinia = createPinia()
let initialized = false

export function useStore() {
  if (!initialized) {
    setActivePinia(pinia)
    initialized = true
  }
  return useUserStore()
}
