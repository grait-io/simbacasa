import { defineComponent, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from './store/user';
import './style.css'; // Import the centralized styles
export default defineComponent({
    name: 'App',
    setup() {
        const isDarkTheme = ref(false);
        const userStore = useUserStore();
        const { telegramUsername } = storeToRefs(userStore);
        onMounted(() => {
            // Ensure Telegram WebApp is available
            if (window.Telegram?.WebApp) {
                const tg = window.Telegram.WebApp;
                // Set the header color
                tg.setHeaderColor?.(tg.headerColor);
                // Set the background color
                tg.setBackgroundColor?.(tg.backgroundColor);
                // Check if dark theme is enabled
                isDarkTheme.value = tg.colorScheme === 'dark';
                // Listen for theme changes
                tg.onEvent?.('themeChanged', () => {
                    isDarkTheme.value = tg.colorScheme === 'dark';
                });
                // Set Telegram username
                userStore.setTelegramUsername();
                console.log('Telegram username after setting:', telegramUsername.value);
            }
            else {
                console.log('Telegram WebApp not available');
            }
        });
        return {
            isDarkTheme,
            telegramUsername
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
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ id: ("app"), ...{ class: (({ 'dark-theme': __VLS_ctx.isDarkTheme })) }, });
    const __VLS_0 = __VLS_resolvedLocalAndGlobalComponents.RouterView;
    /** @type { [typeof __VLS_components.RouterView, typeof __VLS_components.routerView, typeof __VLS_components.RouterView, typeof __VLS_components.routerView, ] } */
    // @ts-ignore
    const __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0({}));
    const __VLS_2 = __VLS_1({}, ...__VLS_functionalComponentArgsRest(__VLS_1));
    __VLS_styleScopedClasses['dark-theme'];
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
//# sourceMappingURL=App.vue.js.map