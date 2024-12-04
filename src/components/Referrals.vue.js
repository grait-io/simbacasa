import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
export default defineComponent({
    name: 'Referrals',
    setup() {
        const router = useRouter();
        const userStore = useUserStore();
        const referralSource = ref('');
        const error = ref('');
        const isSubmitting = ref(false);
        onMounted(() => {
            userStore.setTelegramUsername();
            console.log('Component mounted. Telegram username:', userStore.telegramUsername);
            console.log('Current user store state:', userStore.$state);
        });
        const handleSubmit = async () => {
            error.value = '';
            isSubmitting.value = true;
            window.scrollTo({ top: 0, behavior: 'smooth' });
            userStore.updateUserData({ referralSource: referralSource.value });
            router.push('/photo');
            isSubmitting.value = false;
        };
        const handleBack = () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
            router.back();
        };
        const handleOutsideClick = (event) => {
            const target = event.target;
            if (!target.closest('input')) {
                const activeElement = document.activeElement;
                activeElement?.blur?.();
            }
        };
        return { referralSource, handleSubmit, handleBack, error, isSubmitting, handleOutsideClick };
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
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ onClick: (__VLS_ctx.handleOutsideClick) }, ...{ class: ("content-wrapper") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleBack) }, ...{ class: ("back-button") }, "aria-label": ("Go back"), });
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("referrals") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleBack) }, ...{ class: ("back-button") }, "aria-label": ("Go back"), });
    __VLS_elementAsFunction(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({ ...{ class: ("arrow") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("grey") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.input, __VLS_intrinsicElements.input)({ value: ((__VLS_ctx.referralSource)), type: ("text"), placeholder: ("Referral Source"), });
    if (__VLS_ctx.error) {
        __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("error-message") }, });
        (__VLS_ctx.error);
    }
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("button-container") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleSubmit) }, ...{ class: ("primary-button") }, disabled: ((__VLS_ctx.isSubmitting)), });
    (__VLS_ctx.isSubmitting ? 'Submitting...' : 'Continue');
    __VLS_styleScopedClasses['content-wrapper'];
    __VLS_styleScopedClasses['back-button'];
    __VLS_styleScopedClasses['referrals'];
    __VLS_styleScopedClasses['back-button'];
    __VLS_styleScopedClasses['arrow'];
    __VLS_styleScopedClasses['grey'];
    __VLS_styleScopedClasses['error-message'];
    __VLS_styleScopedClasses['button-container'];
    __VLS_styleScopedClasses['primary-button'];
    var __VLS_slots;
    var __VLS_inheritedAttrs;
    const __VLS_refs = {};
    var $refs;
    return {
        slots: __VLS_slots,
        refs: $refs,
        attrs: {},
    };
}
;
let __VLS_self;
//# sourceMappingURL=Referrals.vue.js.map