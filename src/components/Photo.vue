<template>
  <div class="content-wrapper">
    <div class="photo">
      <h2>Verification Photo</h2>
      <p class="title">Please take a photo of yourself</p>
      <p>This helps us verify your identity.</p>
      
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
        <div class="preview-buttons">
          <button @click="retakePhoto" class="secondary-button">
            Retake Photo
          </button>
          <button @click="handleSubmit" class="primary-button" :disabled="isSubmitting">
            {{ isSubmitting ? 'Uploading...' : 'Continue' }}
          </button>
        </div>
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
    <div class="button-container" v-if="!capturedImage">
      <button @click="handleBack" class="back-button">
        Back
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import tg from '../telegram'

const TABLE_ID = 'tblmd41XoXrQFYtezww'
const API_TOKEN = 'teable_accwindRYobD2azy8ne_O83Or+XMAmIdRe4c5xEcWS7NDkYw9K20rF6O8+XqnbA='

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
        // Get Telegram ID
        const telegramID = String(tg.initDataUnsafe?.user?.id || userStore.telegramUsername || 'temp_' + Math.random().toString(36).substr(2, 9))

        // First create the record without the photo
        console.log('Creating record...')
        const createRecordResponse = await fetch(`https://teable.grait.io/api/table/${TABLE_ID}/record`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${API_TOKEN}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            records: [{
              fields: {
                "First name": String(userStore.$state.firstName),
                "Last Name": String(userStore.$state.lastName),
                "Instagram": String(userStore.$state.instagram),
                "Referral Source": String(userStore.$state.referralSource),
                "Questions answered": String(userStore.$state.questionsAndAnswers),
                "status": "pending",
                "telegramID": telegramID
              }
            }]
          })
        })

        if (!createRecordResponse.ok) {
          throw new Error('Failed to create record')
        }

        const recordData = await createRecordResponse.json()
        const recordId = recordData.records[0].id
        console.log('Record created with ID:', recordId)

        // Convert base64 to blob
        console.log('Converting image to blob...')
        const response = await fetch(capturedImage.value)
        const blob = await response.blob()

        // Create FormData with the blob
        const formData = new FormData()
        formData.append('file', blob, 'verification.jpg')

        // Try to upload the attachment but don't throw on error
        console.log('Uploading attachment...')
        try {
          const attachmentResponse = await fetch(`https://teable.grait.io/api/table/${TABLE_ID}/record/${recordId}/attachment`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${API_TOKEN}`
            },
            body: formData
          })

          if (attachmentResponse.ok) {
            const attachmentData = await attachmentResponse.json()
            console.log('Attachment uploaded:', attachmentData)

            // Try to update the record with the attachment ID
            try {
              const updateResponse = await fetch(`https://teable.grait.io/api/table/${TABLE_ID}/record/${recordId}`, {
                method: 'PATCH',
                headers: {
                  'Authorization': `Bearer ${API_TOKEN}`,
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                  fields: {
                    Photo: [attachmentData.id]
                  }
                })
              })

              if (updateResponse.ok) {
                console.log('Record updated with attachment')
              } else {
                console.log('Failed to update record with attachment, continuing anyway')
              }
            } catch (updateErr) {
              console.log('Error updating record with attachment, continuing anyway:', updateErr)
            }
          } else {
            console.log('Failed to upload attachment, continuing anyway')
          }
        } catch (attachmentErr) {
          console.log('Error uploading attachment, continuing anyway:', attachmentErr)
        }

        // Continue to confirmation regardless of attachment success
        router.push('/confirmation')
      } catch (err) {
        console.error('Error:', err)
        error.value = 'Failed to save data. Please try again.'
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

.preview-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  width: 100%;
}

.secondary-button {
  background-color: var(--tg-theme-secondary-bg-color, #f0f0f0);
  color: var(--tg-theme-text-color, #000000);
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
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

.button-container {
  margin-top: auto;
  padding: 16px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
