import { defineComponent, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
export default defineComponent({
    name: 'Socials',
    setup() {
        const router = useRouter();
        const userStore = useUserStore();
        const instagram = ref('');
        const linkedin = ref('');
        const linkedinInput = ref(null);
        const isFormValid = computed(() => {
            return instagram.value.trim() !== '' || linkedin.value.trim() !== '';
        });
        const handleSubmit = () => {
            if (isFormValid.value) {
                window.scrollTo({ top: 0, behavior: 'smooth' });
                userStore.updateUserData({ instagram: instagram.value, linkedin: linkedin.value });
                router.push('/questions');
            }
        };
        const handleBack = () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
            router.back();
        };
        const focusLinkedin = () => {
            if (linkedinInput.value) {
                linkedinInput.value.focus();
            }
        };
        const handleOutsideClick = (event) => {
            const target = event.target;
            if (!target.closest('input')) {
                const activeElement = document.activeElement;
                activeElement?.blur?.();
            }
        };
        return {
            instagram,
            linkedin,
            handleSubmit,
            handleBack,
            linkedinInput,
            focusLinkedin,
            isFormValid,
            handleOutsideClick
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
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ onClick: (__VLS_ctx.handleOutsideClick) }, ...{ class: ("content-wrapper") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("socials") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("header") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleBack) }, ...{ class: ("back-button") }, "aria-label": ("Go back"), });
    __VLS_elementAsFunction(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({ ...{ class: ("arrow") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("grey") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.input, __VLS_intrinsicElements.input)({ ...{ onKeydown: (__VLS_ctx.focusLinkedin) }, value: ((__VLS_ctx.instagram)), type: ("text"), placeholder: ("Instagram"), });
    __VLS_elementAsFunction(__VLS_intrinsicElements.input, __VLS_intrinsicElements.input)({ value: ((__VLS_ctx.linkedin)), type: ("text"), placeholder: ("LinkedIn"), ref: ("linkedinInput"), });
    // @ts-ignore navigation for `const linkedinInput = ref()`
    __VLS_ctx.linkedinInput;
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("button-container") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleSubmit) }, ...{ class: ("primary-button") }, disabled: ((!__VLS_ctx.isFormValid)), });
    __VLS_styleScopedClasses['content-wrapper'];
    __VLS_styleScopedClasses['socials'];
    __VLS_styleScopedClasses['header'];
    __VLS_styleScopedClasses['back-button'];
    __VLS_styleScopedClasses['arrow'];
    __VLS_styleScopedClasses['grey'];
    __VLS_styleScopedClasses['button-container'];
    __VLS_styleScopedClasses['primary-button'];
    var __VLS_slots;
    var __VLS_inheritedAttrs;
    const __VLS_refs = {
        "linkedinInput": __VLS_nativeElements['input'],
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
//# sourceMappingURL=Socials.vue.js.map