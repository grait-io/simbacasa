import { defineComponent, ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
import tg from '../telegram';
const TABLE_ID = 'tbliWkyKE4dT2L9s1oM';
const FIELD_ID = 'fldtPf6h96XFllw4sOM'; // where the picture is stored
const API_TOKEN = 'teable_accO8ibvH9yrZjyRH8C_xEua4r2Cre7YHIZMuO3s7tazZWJSUBOP+dO4uZqkV9k=';
export default defineComponent({
    name: 'Photo',
    setup() {
        const router = useRouter();
        const userStore = useUserStore();
        const video = ref(null);
        const canvas = ref(null);
        const stream = ref(null);
        const capturedImage = ref(null);
        const error = ref('');
        const isSubmitting = ref(false);
        const isCameraReady = ref(false);
        const onVideoLoaded = () => {
            console.log('Video element loaded');
            if (video.value) {
                console.log('Video dimensions:', {
                    width: video.value.videoWidth,
                    height: video.value.videoHeight
                });
                isCameraReady.value = true;
            }
        };
        const initCamera = async () => {
            console.log('Initializing camera...');
            try {
                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    throw new Error('Camera API not supported');
                }
                // Ensure canvas is ready
                if (!canvas.value) {
                    throw new Error('Canvas element not initialized');
                }
                stream.value = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: 'user',
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    },
                    audio: false
                });
                console.log('Camera stream obtained');
                if (video.value && stream.value) {
                    video.value.srcObject = stream.value;
                    console.log('Stream attached to video element');
                    // Ensure video plays
                    try {
                        await video.value.play();
                        console.log('Video playback started');
                    }
                    catch (playError) {
                        console.error('Error playing video:', playError);
                        error.value = 'Failed to start video playback';
                    }
                }
                else {
                    console.error('Video element or stream not available');
                    error.value = 'Camera initialization failed';
                }
            }
            catch (err) {
                console.error('Camera initialization error:', err);
                error.value = `Failed to access camera: ${err instanceof Error ? err.message : 'Unknown error'}`;
            }
        };
        const capturePhoto = () => {
            console.log('Capturing photo...');
            // Double check canvas exists
            if (!canvas.value) {
                console.error('Canvas element not found');
                error.value = 'Failed to initialize capture system';
                return;
            }
            if (!video.value || !isCameraReady.value) {
                console.error('Cannot capture: video or camera not ready', {
                    video: !!video.value,
                    canvas: !!canvas.value,
                    isCameraReady: isCameraReady.value
                });
                return;
            }
            const context = canvas.value.getContext('2d');
            if (!context) {
                console.error('Failed to get canvas context');
                error.value = 'Failed to initialize capture system';
                return;
            }
            try {
                // Set canvas size to match video dimensions
                const videoWidth = video.value.videoWidth;
                const videoHeight = video.value.videoHeight;
                console.log('Setting canvas dimensions:', { videoWidth, videoHeight });
                canvas.value.width = videoWidth;
                canvas.value.height = videoHeight;
                // Draw the video frame to the canvas
                context.drawImage(video.value, 0, 0, videoWidth, videoHeight);
                // Convert to JPEG
                const imageData = canvas.value.toDataURL('image/jpeg', 0.8);
                console.log('Photo captured successfully');
                capturedImage.value = imageData;
                // Stop the camera stream
                if (stream.value) {
                    stream.value.getTracks().forEach(track => {
                        track.stop();
                        console.log('Camera track stopped');
                    });
                    stream.value = null;
                }
            }
            catch (err) {
                console.error('Error capturing photo:', err);
                error.value = 'Failed to capture photo';
            }
        };
        const retakePhoto = () => {
            console.log('Retaking photo...');
            capturedImage.value = null;
            error.value = '';
            initCamera();
        };
        const handleSubmit = async () => {
            if (!capturedImage.value) {
                console.error('No image captured');
                return;
            }
            isSubmitting.value = true;
            error.value = '';
            try {
                // Get Telegram ID
                const telegramID = String(tg.initDataUnsafe?.user?.id || userStore.telegramUsername || 'temp_' + Math.random().toString(36).substr(2, 9));
                // First create the record without the photo
                console.log('Creating record...');
                const createRecordUrl = new URL(`https://teable.grait.io/api/table/${TABLE_ID}/record`);
                createRecordUrl.searchParams.append('fieldKeyType', 'id');
                const createRecordResponse = await fetch(createRecordUrl, {
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
                                    "Referral Source": String(userStore.$state.referralSource),
                                    "Questions answered": String(userStore.$state.questionsAndAnswers),
                                    "status": "pending",
                                    "telegramID": telegramID
                                }
                            }]
                    })
                });
                if (!createRecordResponse.ok) {
                    throw new Error('Failed to create record');
                }
                const recordData = await createRecordResponse.json();
                const recordId = recordData.records[0].id;
                console.log('Record created with ID:', recordId);
                // Convert base64 to blob
                console.log('Converting image to blob...');
                const response = await fetch(capturedImage.value);
                const blob = await response.blob();
                // Create FormData and append the file
                const formData = new FormData();
                formData.append('file', blob, 'verification.jpg');
                formData.append('fileUrl', ''); // Optional parameter from Swagger spec
                // Upload the attachment using the correct endpoint
                console.log('Uploading attachment...');
                const uploadUrl = new URL(`https://teable.simbacasa.com/api/table/${TABLE_ID}/record/${recordId}/${FIELD_ID}/uploadAttachment`);
                uploadUrl.searchParams.append('fieldKeyType', 'id');
                console.log('Upload URL:', uploadUrl.toString());
                const attachmentResponse = await fetch(uploadUrl, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${API_TOKEN}`,
                        'Accept': 'application/json'
                    },
                    body: formData
                });
                if (!attachmentResponse.ok) {
                    const errorData = await attachmentResponse.json().catch(() => ({}));
                    console.error('Upload failed:', errorData);
                    throw new Error(`Failed to upload attachment: ${attachmentResponse.status}`);
                }
                const attachmentData = await attachmentResponse.json();
                console.log('Attachment uploaded successfully:', attachmentData);
                // Continue to confirmation
                router.push('/confirmation');
            }
            catch (err) {
                console.error('Error:', err);
                error.value = err instanceof Error ? err.message : 'Failed to save data. Please try again.';
            }
            finally {
                isSubmitting.value = false;
            }
        };
        const handleBack = () => {
            if (stream.value) {
                stream.value.getTracks().forEach(track => track.stop());
            }
            router.back();
        };
        onMounted(() => {
            console.log('Component mounted');
            // Ensure canvas is available
            if (!canvas.value) {
                console.error('Canvas not mounted');
                error.value = 'Failed to initialize capture system';
                return;
            }
            initCamera();
        });
        onUnmounted(() => {
            console.log('Component unmounting');
            if (stream.value) {
                stream.value.getTracks().forEach(track => track.stop());
            }
        });
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
        };
    }
});
function __VLS_template() {
    const __VLS_ctx = {};
    const __VLS_localComponents = {
        ...{},
        ...{},
        ...__VLS_ctx,
    };
    let __VLS_components;
    const __VLS_localDirectives = {
        ...{},
        ...__VLS_ctx,
    };
    let __VLS_directives;
    let __VLS_styleScopedClasses;
    // CSS variable injection 
    // CSS variable injection end 
    let __VLS_resolvedLocalAndGlobalComponents;
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("content-wrapper") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleBack) }, ...{ class: ("back-button") }, "aria-label": ("Go back"), });
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("photo") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("grey") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.br, __VLS_intrinsicElements.br)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.br, __VLS_intrinsicElements.br)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.canvas, __VLS_intrinsicElements.canvas)({ ref: ("canvas"), ...{ style: ({}) }, });
    // @ts-ignore navigation for `const canvas = ref()`
    __VLS_ctx.canvas;
    if (!__VLS_ctx.capturedImage) {
        __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("camera-container") }, });
        __VLS_elementAsFunction(__VLS_intrinsicElements.video, __VLS_intrinsicElements.video)({ ...{ onLoadedmetadata: (__VLS_ctx.onVideoLoaded) }, ref: ("video"), autoplay: (true), playsinline: (true), ...{ style: ({}) }, });
        // @ts-ignore navigation for `const video = ref()`
        __VLS_ctx.video;
        __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("camera-controls") }, });
        __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.capturePhoto) }, ...{ class: ("capture-button") }, disabled: ((!__VLS_ctx.isCameraReady)), });
        __VLS_elementAsFunction(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({ ...{ class: ("camera-icon") }, });
        if (!__VLS_ctx.isCameraReady) {
            __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("status-message") }, });
        }
    }
    else {
        __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("preview-container") }, });
        __VLS_elementAsFunction(__VLS_intrinsicElements.img, __VLS_intrinsicElements.img)({ src: ((__VLS_ctx.capturedImage)), alt: ("Captured photo"), ...{ class: ("preview-image") }, });
        __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("button-container") }, });
        __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleSubmit) }, ...{ class: ("primary-button") }, disabled: ((__VLS_ctx.isSubmitting)), });
        (__VLS_ctx.isSubmitting ? 'Uploading...' : 'Continue');
    }
    if (__VLS_ctx.error) {
        __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("error-message") }, });
        (__VLS_ctx.error);
    }
    if (!__VLS_ctx.capturedImage) {
        __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("button-container") }, });
        __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.capturePhoto) }, ...{ class: ("primary-button") }, disabled: ((!__VLS_ctx.isCameraReady)), });
    }
    __VLS_styleScopedClasses['content-wrapper'];
    __VLS_styleScopedClasses['back-button'];
    __VLS_styleScopedClasses['photo'];
    __VLS_styleScopedClasses['grey'];
    __VLS_styleScopedClasses['camera-container'];
    __VLS_styleScopedClasses['camera-controls'];
    __VLS_styleScopedClasses['capture-button'];
    __VLS_styleScopedClasses['camera-icon'];
    __VLS_styleScopedClasses['status-message'];
    __VLS_styleScopedClasses['preview-container'];
    __VLS_styleScopedClasses['preview-image'];
    __VLS_styleScopedClasses['button-container'];
    __VLS_styleScopedClasses['primary-button'];
    __VLS_styleScopedClasses['error-message'];
    __VLS_styleScopedClasses['button-container'];
    __VLS_styleScopedClasses['primary-button'];
    var __VLS_slots;
    var __VLS_inheritedAttrs;
    const __VLS_refs = {
        "canvas": __VLS_nativeElements['canvas'],
        "video": __VLS_nativeElements['video'],
    };
    var $refs;
    return {
        slots: __VLS_slots,
        refs: $refs,
        attrs: {},
    };
}
;
let __VLS_self;
//# sourceMappingURL=Photo.vue.js.map