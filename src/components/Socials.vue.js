import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
export default defineComponent({
    name: 'Socials',
    setup() {
        const router = useRouter();
        const userStore = useUserStore();
        const instagram = ref('');
        const linkedin = ref('');
        const handleSubmit = () => {
            userStore.updateUserData({ instagram: instagram.value, linkedin: linkedin.value });
            router.push('/about-you');
        };
        return { instagram, linkedin, handleSubmit };
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
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("socials") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.input, __VLS_intrinsicElements.input)({ value: ((__VLS_ctx.instagram)), type: ("text"), placeholder: ("Instagram"), });
    __VLS_elementAsFunction(__VLS_intrinsicElements.input, __VLS_intrinsicElements.input)({ value: ((__VLS_ctx.linkedin)), type: ("text"), placeholder: ("LinkedIn"), });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleSubmit) }, ...{ class: ("primary-button") }, });
    __VLS_styleScopedClasses['socials'];
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
//# sourceMappingURL=Socials.vue.js.map