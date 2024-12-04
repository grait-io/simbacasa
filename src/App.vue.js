import { defineComponent, onMounted, ref, computed } from 'vue';
import { useUserStore } from './store/user';
import { useRoute } from 'vue-router';
import './style.css'; // Import the centralized styles
export default defineComponent({
    name: 'App',
    setup() {
        // Initialize store immediately in setup
        const userStore = useUserStore();
        const telegramUsername = ref('');
        const route = useRoute();
        const isWelcomePage = computed(() => {
            return route.path === '/' || route.path === '/welcome';
        });
        onMounted(() => {
            // Ensure Telegram WebApp is available
            if (window.Telegram?.WebApp) {
                const tg = window.Telegram.WebApp;
                // Force light theme colors
                tg.setHeaderColor?.('#FDFCF8');
                tg.setBackgroundColor?.('#FDFCF8');
                // Set Telegram username
                userStore.setTelegramUsername();
                telegramUsername.value = userStore.telegramUsername;
            }
            else {
                console.log('Telegram WebApp not available');
            }
        });
        return {
            telegramUsername,
            isWelcomePage
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
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ id: ("app"), });
    if (!__VLS_ctx.isWelcomePage) {
        __VLS_elementAsFunction(__VLS_intrinsicElements.img)({ src: ("/logo.svg"), alt: ("Logo"), ...{ class: ("app-logo") }, });
    }
    const __VLS_0 = __VLS_resolvedLocalAndGlobalComponents.RouterView;
    /** @type { [typeof __VLS_components.RouterView, typeof __VLS_components.routerView, typeof __VLS_components.RouterView, typeof __VLS_components.routerView, ] } */
    // @ts-ignore
    const __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0({}));
    const __VLS_2 = __VLS_1({}, ...__VLS_functionalComponentArgsRest(__VLS_1));
    __VLS_styleScopedClasses['app-logo'];
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