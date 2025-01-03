import { defineComponent, onMounted } from 'vue';
import { useRouter } from 'vue-router';
export default defineComponent({
    name: 'Welcome',
    setup() {
        const router = useRouter();
        const tg = window.Telegram.WebApp;
        const handleGetStarted = () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
            try {
                tg.HapticFeedback?.impactOccurred?.('medium');
            }
            catch (e) {
                console.log('HapticFeedback not available');
            }
            router.push('/name');
        };
        onMounted(() => {
            try {
                tg.ready?.();
                tg.expand?.();
            }
            catch (e) {
                console.log('Telegram WebApp not fully available');
            }
        });
        return { handleGetStarted };
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
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("welcome") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("content") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.img, __VLS_intrinsicElements.img)({ src: ("/logo.svg"), alt: ("SimbiCasa Logo"), ...{ class: ("logo centered-logo") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.br, __VLS_intrinsicElements.br)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.b, __VLS_intrinsicElements.b)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("grey") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.br)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("button-container") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleGetStarted) }, ...{ class: ("primary-button") }, });
    __VLS_styleScopedClasses['content-wrapper'];
    __VLS_styleScopedClasses['welcome'];
    __VLS_styleScopedClasses['content'];
    __VLS_styleScopedClasses['logo'];
    __VLS_styleScopedClasses['centered-logo'];
    __VLS_styleScopedClasses['grey'];
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
//# sourceMappingURL=Welcome.vue.js.map