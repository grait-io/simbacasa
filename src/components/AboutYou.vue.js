import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
export default defineComponent({
    name: 'AboutYou',
    setup() {
        const router = useRouter();
        const userStore = useUserStore();
        const about = ref('');
        const aboutTextarea = ref(null);
        const handleSubmit = () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
            userStore.updateUserData({ about: about.value });
            router.push('/questions');
        };
        const handleBack = () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
            router.back();
        };
        const handleOutsideClick = (event) => {
            const target = event.target;
            if (!target.closest('textarea')) {
                const activeElement = document.activeElement;
                activeElement?.blur?.();
            }
        };
        return { about, handleSubmit, handleBack, aboutTextarea, handleOutsideClick };
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
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("about-you") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("title") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.textarea, __VLS_intrinsicElements.textarea)({ value: ((__VLS_ctx.about)), placeholder: ("About you"), maxlength: ("200"), ref: ("aboutTextarea"), });
    // @ts-ignore navigation for `const aboutTextarea = ref()`
    __VLS_ctx.aboutTextarea;
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("button-container") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleSubmit) }, ...{ class: ("primary-button") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleBack) }, ...{ class: ("back-button") }, });
    __VLS_styleScopedClasses['content-wrapper'];
    __VLS_styleScopedClasses['about-you'];
    __VLS_styleScopedClasses['title'];
    __VLS_styleScopedClasses['button-container'];
    __VLS_styleScopedClasses['primary-button'];
    __VLS_styleScopedClasses['back-button'];
    var __VLS_slots;
    var __VLS_inheritedAttrs;
    const __VLS_refs = {
        "aboutTextarea": __VLS_nativeElements['textarea'],
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
//# sourceMappingURL=AboutYou.vue.js.map