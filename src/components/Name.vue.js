import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
export default defineComponent({
    name: 'Name',
    setup() {
        const router = useRouter();
        const userStore = useUserStore();
        const tg = window.Telegram.WebApp;
        const firstName = ref('');
        const lastName = ref('');
        const lastNameInput = ref(null);
        const isFormValid = computed(() => firstName.value.trim() && lastName.value.trim());
        const handleSubmit = () => {
            if (isFormValid.value) {
                window.scrollTo({ top: 0, behavior: 'smooth' });
                userStore.updateUserData({ firstName: firstName.value, lastName: lastName.value });
                tg.HapticFeedback.impactOccurred('medium');
                router.push('/socials');
            }
        };
        const focusLastName = () => {
            if (lastNameInput.value) {
                lastNameInput.value.focus();
            }
        };
        const handleOutsideClick = (event) => {
            const target = event.target;
            if (!target.closest('input')) {
                const activeElement = document.activeElement;
                activeElement?.blur?.();
            }
        };
        onMounted(() => {
            tg.ready();
            tg.expand();
        });
        return { firstName, lastName, handleSubmit, isFormValid, lastNameInput, focusLastName, handleOutsideClick };
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
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("name") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("title") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.input, __VLS_intrinsicElements.input)({ ...{ onKeydown: (__VLS_ctx.focusLastName) }, value: ((__VLS_ctx.firstName)), type: ("text"), placeholder: ("First Name"), });
    __VLS_elementAsFunction(__VLS_intrinsicElements.input, __VLS_intrinsicElements.input)({ ...{ onKeydown: (__VLS_ctx.handleSubmit) }, value: ((__VLS_ctx.lastName)), type: ("text"), placeholder: ("Last Name"), ref: ("lastNameInput"), });
    // @ts-ignore navigation for `const lastNameInput = ref()`
    __VLS_ctx.lastNameInput;
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("button-container") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleSubmit) }, ...{ class: ("primary-button") }, disabled: ((!__VLS_ctx.isFormValid)), });
    __VLS_styleScopedClasses['content-wrapper'];
    __VLS_styleScopedClasses['name'];
    __VLS_styleScopedClasses['title'];
    __VLS_styleScopedClasses['button-container'];
    __VLS_styleScopedClasses['primary-button'];
    var __VLS_slots;
    var __VLS_inheritedAttrs;
    const __VLS_refs = {
        "lastNameInput": __VLS_nativeElements['input'],
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
//# sourceMappingURL=Name.vue.js.map