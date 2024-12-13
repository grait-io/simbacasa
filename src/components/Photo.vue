<template>
  <div class="content-wrapper">
    <button @click="handleBack" class="back-button" aria-label="Go back"></button>
    <div class="photo">
      <p>📷  &nbsp;Verification Photo</p>
      
      <p class="grey">Please take a photo of yourself.<br>
        
        <br>
      This photo will be only used to verify your identity.</p>
      
      <!-- Always render canvas but keep it hidden -->
      <canvas ref="canvas" style="display: none;"></canvas>
      
      <div class="camera-container" v-if="!capturedImage">
        <video 
          ref="video" 
          autoplay 
          playsinline 
          style="width: 100%; height: auto;"
          @loadedmetadata="onVideoLoaded"
        ></video>
        <div class="camera-controls">
          <button @click="capturePhoto" class="capture-button" :disabled="!isCameraReady">
            <span class="camera-icon">📸</span>
          </button>
        </div>
        <p v-if="!isCameraReady" class="status-message">
          Initializing camera...
        </p>
      </div>

      <div class="preview-container" v-else>
        <img :src="capturedImage" alt="Captured photo" class="preview-image">
        <div class="button-container">
          <button @click="handleSubmit" class="primary-button" :disabled="isSubmitting">
            {{ isSubmitting ? 'Uploading...' : 'Continue' }}
          </button>
          <button @click="retakePhoto" class="secondary-button">
            Retake Photo
          </button>
        </div>
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
    <div v-if="!capturedImage" class="button-container">
      <button @click="capturePhoto" class="primary-button" :disabled="!isCameraReady">
        Take Photo
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import tg from '../telegram'

const TABLE_ID = 'tbliWkyKE4dT2L9s1oM'
const FIELD_ID = 'fldtPf6h96XFllw4sOM' // where the picture is stored
const API_TOKEN = 'teable_accO8ibvH9yrZjyRH8C_xEua4r2Cre7YHIZMuO3s7tazZWJSUBOP+dO4uZqkV9k='
const RECEIVED_WEBHOOK_URL = import.meta.env.VITE_RECEIVED_WEBHOOK_URL || 'https://n8n.simbacasa.com/webhook-test/app-received'

export default defineComponent({
  name: 'Photo',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const video = ref<HTMLVideoElement | null>(null)
    const canvas = ref<HTMLCanvasElement | null>(null)
    const stream = ref<MediaStream | null>(null)
    const capturedImage = ref<string | null>(null)
    const error = ref('')
    const isSubmitting = ref(false)
    const isCameraReady = ref(false)

    const sendReceivedWebhook = async (telegramID: string, name: string) => {
      console.log('Sending received webhook with the following details:', {
        url: RECEIVED_WEBHOOK_URL,
        telegramID,
        name
      })

      try {
        const payload = {
          telegramID,
          name: `${userStore.$state.firstName} ${userStore.$state.lastName}`
        }

        console.log('Webhook payload:', JSON.stringify(payload, null, 2))

        const response = await fetch(RECEIVED_WEBHOOK_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload)
        })

        console.log('Webhook response status:', response.status)
        
        // TypeScript-friendly way to log headers
        const headerObj: Record<string, string> = {}
        response.headers.forEach((value, key) => {
          headerObj[key] = value
        })
        console.log('Webhook response headers:', headerObj)

        const responseText = await response.text()
        console.log('Webhook response body:', responseText)

        if (!response.ok) {
          console.error('Failed to send received webhook', responseText)
          throw new Error(`Webhook call failed with status ${response.status}: ${responseText}`)
        }
      } catch (err) {
        console.error('Error sending received webhook:', err)
        throw err  // Re-throw to allow caller to handle the error
      }
    }

    const onVideoLoaded = () => {
      console.log('Video element loaded')
      if (video.value) {
        console.log('Video dimensions:', {
          width: video.value.videoWidth,
          height: video.value.videoHeight
        })
        isCameraReady.value = true
      }
    }

    const initCamera = async () => {
      console.log('Initializing camera...')
      try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          throw new Error('Camera API not supported')
        }

        // Ensure canvas is ready
        if (!canvas.value) {
          throw new Error('Canvas element not initialized')
        }

        stream.value = await navigator.mediaDevices.getUserMedia({
          video: { 
            facingMode: 'user',
            width: { ideal: 1280 },
            height: { ideal: 720 }
          },
          audio: false
        })
        
        console.log('Camera stream obtained')
        
        if (video.value && stream.value) {
          video.value.srcObject = stream.value
          console.log('Stream attached to video element')
          
          // Ensure video plays
          try {
            await video.value.play()
            console.log('Video playback started')
          } catch (playError) {
            console.error('Error playing video:', playError)
            error.value = 'Failed to start video playback'
          }
        } else {
          console.error('Video element or stream not available')
          error.value = 'Camera initialization failed'
        }
      } catch (err) {
        console.error('Camera initialization error:', err)
        error.value = `Failed to access camera: ${err instanceof Error ? err.message : 'Unknown error'}`
      }
    }

    const capturePhoto = () => {
      console.log('Capturing photo...')
      
      // Double check canvas exists
      if (!canvas.value) {
        console.error('Canvas element not found')
        error.value = 'Failed to initialize capture system'
        return
      }

      if (!video.value || !isCameraReady.value) {
        console.error('Cannot capture: video or camera not ready', {
          video: !!video.value,
          canvas: !!canvas.value,
          isCameraReady: isCameraReady.value
        })
        return
      }
      
      const context = canvas.value.getContext('2d')
      if (!context) {
        console.error('Failed to get canvas context')
        error.value = 'Failed to initialize capture system'
        return
      }

      try {
        // Set canvas size to match video dimensions
        const videoWidth = video.value.videoWidth
        const videoHeight = video.value.videoHeight
        console.log('Setting canvas dimensions:', { videoWidth, videoHeight })
        
        canvas.value.width = videoWidth
        canvas.value.height = videoHeight
        
        // Draw the video frame to the canvas
        context.drawImage(video.value, 0, 0, videoWidth, videoHeight)
        
        // Convert to JPEG
        const imageData = canvas.value.toDataURL('image/jpeg', 0.8)
        console.log('Photo captured successfully')
        
        capturedImage.value = imageData
        
        // Stop the camera stream
        if (stream.value) {
          stream.value.getTracks().forEach(track => {
            track.stop()
            console.log('Camera track stopped')
          })
          stream.value = null
        }
      } catch (err) {
        console.error('Error capturing photo:', err)
        error.value = 'Failed to capture photo'
      }
    }

    const retakePhoto = () => {
      console.log('Retaking photo...')
      capturedImage.value = null
      error.value = ''
      initCamera()
    }

    const handleSubmit = async () => {
      if (!capturedImage.value) {
        console.error('No image captured')
        return
      }
      
      isSubmitting.value = true
      error.value = ''

      try {
        // Get Telegram ID and username
        const telegramID = String(tg.initDataUnsafe?.user?.id || 'temp_' + Math.random().toString(36).substr(2, 9))
        const telegramUsername = userStore.telegramUsername || tg.initDataUnsafe?.user?.username || ''

        // First create the record without the photo
        console.log('Creating record...')
        const createRecordUrl = `https://teable.simbacasa.com/api/table/${TABLE_ID}/record`
        const queryParams = new URLSearchParams({ fieldKeyType: 'id' })
        const fullUrl = `${createRecordUrl}?${queryParams.toString()}`

        // Ensure LinkedIn URL is properly formatted
        let linkedinUrl = userStore.$state.linkedin
        if (linkedinUrl && !linkedinUrl.startsWith('https://')) {
          linkedinUrl = `https://www.linkedin.com/in/${linkedinUrl.replace(/^.*\/in\//, '')}`
        }

        const createRecordResponse = await fetch(fullUrl, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${API_TOKEN}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            records: [{
              fields: {
                "First name": String(userStore.$state.firstName),
                "Last Name": String(userStore.$state.lastName),
                "Instagram": String(userStore.$state.instagram),
                "LinkedIn": linkedinUrl,
                "Referral Source": String(userStore.$state.referralSource),
                "Questions answered": String(userStore.$state.questionsAndAnswers),
                "status": "pending",
                "telegramID": telegramID,
                "telegramUsername": telegramUsername  // Added telegramUsername field
              }
            }]
          })
        })

        if (!createRecordResponse.ok) {
          const errorData = await createRecordResponse.json().catch(() => ({}))
          console.error('Create record failed:', errorData)
          throw new Error(`Failed to create record: ${createRecordResponse.status}`)
        }

        const recordData = await createRecordResponse.json()
        const recordId = recordData.records[0].id
        console.log('Record created with ID:', recordId)

        // Send received webhook
        await sendReceivedWebhook(telegramID, `${userStore.$state.firstName} ${userStore.$state.lastName}`)

        // Convert base64 to blob
        console.log('Converting image to blob...')
        const response = await fetch(capturedImage.value)
        const blob = await response.blob()

        // Create FormData and append the file
        const formData = new FormData()
        formData.append('file', blob, 'verification.jpg')
        formData.append('fileUrl', '') // Optional parameter from Swagger spec

        // Upload the attachment using the correct endpoint
        console.log('Uploading attachment...')
        const uploadUrl = `https://teable.simbacasa.com/api/table/${TABLE_ID}/record/${recordId}/${FIELD_ID}/uploadAttachment`
        const uploadQueryParams = new URLSearchParams({ fieldKeyType: 'id' })
        const fullUploadUrl = `${uploadUrl}?${uploadQueryParams.toString()}`
        
        const attachmentResponse = await fetch(fullUploadUrl, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${API_TOKEN}`,
            'Accept': 'application/json'
          },
          body: formData
        })

        if (!attachmentResponse.ok) {
          const errorData = await attachmentResponse.json().catch(() => ({}))
          console.error('Upload failed:', errorData)
          throw new Error(`Failed to upload attachment: ${attachmentResponse.status}`)
        }

        const attachmentData = await attachmentResponse.json()
        console.log('Attachment uploaded successfully:', attachmentData)

        // Continue to confirmation
        router.push('/confirmation')
      } catch (err) {
        console.error('Error:', err)
        error.value = err instanceof Error ? err.message : 'Failed to save data. Please try again.'
      } finally {
        isSubmitting.value = false
      }
    }

    const handleBack = () => {
      if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop())
      }
      router.back()
    }

    onMounted(() => {
      console.log('Component mounted')
      // Ensure canvas is available
      if (!canvas.value) {
        console.error('Canvas not mounted')
        error.value = 'Failed to initialize capture system'
        return
      }
      initCamera()
    })

    onUnmounted(() => {
      console.log('Component unmounting')
      if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop())
      }
    })

    return {
      video,
      canvas,
      capturedImage,
      error,
      isSubmitting,
      isCameraReady,
      onVideoLoaded,
      capturePhoto,
      retakePhoto,
      handleSubmit,
      handleBack
    }
  }
})
</script>

<style>
.photo {
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.camera-container {
  width: 100%;
  max-width: 400px;
  margin: 20px auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
  position: relative;
}

.camera-container video {
  width: 100%;
  height: auto;
  border-radius: 8px;
  background-color: var(--tg-theme-secondary-bg-color, #f0f0f0);
}

.camera-controls {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.capture-button {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: var(--tg-theme-button-color, #3390ec);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: transform 0.2s;
}

.capture-button:active {
  transform: scale(0.95);
}

.camera-icon {
  font-size: 32px;
}

.capture-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.preview-container {
  width: 100%;
  max-width: 400px;
  margin: 20px auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.preview-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
  border: 2px solid var(--tg-theme-button-color, #3390ec);
}

.error-message {
  color: #ff3b30;
  text-align: center;
  margin-top: 16px;
}

.status-message {
  color: var(--tg-theme-hint-color, #999999);
  text-align: center;
  margin-top: 8px;
}

.secondary-button {
  margin-top: 10px;
  background-color: var(--tg-theme-secondary-bg-color, #f0f0f0);
  color: var(--tg-theme-text-color, #000);
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}
</style>
