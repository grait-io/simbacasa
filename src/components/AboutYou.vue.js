import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
export default defineComponent({
    name: 'AboutYou',
    setup() {
        const router = useRouter();
        const userStore = useUserStore();
        const about = ref('');
        const handleSubmit = () => {
            userStore.updateUserData({ about: about.value });
            router.push('/referrals');
        };
        return { about, handleSubmit };
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
    let __VLS_resolvedLocalAndGlobalComponents;
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("about-you") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.textarea, __VLS_intrinsicElements.textarea)({ value: ((__VLS_ctx.about)), placeholder: ("About you"), maxlength: ("200"), });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleSubmit) }, ...{ class: ("primary-button") }, });
    __VLS_styleScopedClasses['about-you'];
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
//# sourceMappingURL=AboutYou.vue.js.map