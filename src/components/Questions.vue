<template>
  <div class="content-wrapper" @click="handleOutsideClick">
    <button @click="handleBack" class="back-button" aria-label="Go back"></button>
    <div class="questions" ref="questionsContainer">
      <p>Questions</p>
      <div v-if="loading" class="loading">Loading questions...</div>
      <div v-else-if="error" class="error-message">{{ error }}</div>
      <div v-else class="questions-list">
        <div v-for="(question, index) in questions" :key="question.id" class="question-item">
          <p class="grey">{{ question.fields.question }}</p>
          <textarea 
            v-model="answers[index]" 
            :placeholder="'Your answer...'"
            rows="3"
          ></textarea>
        </div>
      </div>
    </div>
    <div class="button-container">
      <button @click="handleSubmit" class="primary-button" :disabled="isSubmitting || !canSubmit">
        {{ isSubmitting ? 'Submitting...' : 'Continue' }}
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'

interface Question {
  fields: {
    title: string;
    question: string;
  };
  id: string;
}

export default defineComponent({
  name: 'Questions',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const questions = ref<Question[]>([])
    const answers = ref<string[]>([])
    const loading = ref(true)
    const error = ref('')
    const isSubmitting = ref(false)
    const questionsContainer = ref<HTMLElement | null>(null)

    const canSubmit = computed(() => {
      return answers.value.every(answer => answer && answer.trim().length > 0)
    })

    const fetchQuestions = async () => {
      try {
        const url = new URL("https://teable.grait.io/api/table/tbl1tcysT4sGwT5jmTz/record")
        const response = await fetch(url, {
          method: "GET",
          headers: {
            "Authorization": "Bearer teable_accwindRYobD2azy8ne_O83Or+XMAmIdRe4c5xEcWS7NDkYw9K20rF6O8+XqnbA=",
            "Accept": "application/json"
          }
        })

        if (!response.ok) {
          throw new Error(`Failed to fetch questions: ${response.status}`)
        }

        const data = await response.json()
        questions.value = data.records.filter((record: Question) => 
          record.fields && record.fields.question
        )
        answers.value = new Array(questions.value.length).fill('')
        console.log('Fetched questions:', questions.value)
      } catch (err) {
        error.value = 'Failed to load questions. Please try again later.'
        console.error('Error fetching questions:', err)
      } finally {
        loading.value = false
      }
    }

    const handleSubmit = async () => {
      if (!canSubmit.value) return

      isSubmitting.value = true
      window.scrollTo({ top: 0, behavior: 'smooth' })

      // Format questions and answers as a single string
      const formattedAnswers = questions.value
        .map((q, index) => `${q.fields.question}\n${answers.value[index]}`)
        .join('\n\n')

      console.log('Formatted answers:', formattedAnswers)
      
      // Store the formatted string directly
      userStore.$state.questionsAndAnswers = formattedAnswers

      console.log('Updated user store:', userStore.$state)

      // Navigate to referrals page
      router.push('/referrals')
      isSubmitting.value = false
    }

    const handleBack = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
      router.back()
    }

    const handleOutsideClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('textarea')) {
        const activeElement = document.activeElement as HTMLElement
        activeElement?.blur?.()
      }
    }

    onMounted(() => {
      fetchQuestions()
    })

    return {
      questions,
      answers,
      loading,
      error,
      isSubmitting,
      canSubmit,
      handleSubmit,
      handleBack,
      handleOutsideClick,
      questionsContainer
    }
  }
})
</script>

<style>
.questions {
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.question-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--tg-theme-hint-color, #999999);
  border-radius: 8px;
  background: var(--tg-theme-bg-color, #ffffff);
  color: var(--tg-theme-text-color, #000000);
  font-size: 16px;
  resize: vertical;
  min-height: 100px;
}

textarea:focus {
  outline: none;
  border-color: var(--tg-theme-button-color, #3390ec);
}

.loading {
  text-align: center;
  color: var(--tg-theme-hint-color, #999999);
}

.error-message {
  color: #ff3b30;
  text-align: center;
}
</style>
