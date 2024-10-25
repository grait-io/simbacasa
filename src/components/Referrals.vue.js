import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
import tg from '../telegram';
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
        });
        const handleSubmit = async () => {
            error.value = '';
            isSubmitting.value = true;
            window.scrollTo({ top: 0, behavior: 'smooth' });
            userStore.updateUserData({ referralSource: referralSource.value });
            try {
                console.log('User data before submission:', JSON.stringify(userStore.$state, null, 2));
                console.log('Submitting form with Telegram username:', userStore.telegramUsername);
                const url = new URL("https://teable.grait.io/api/table/tblmd41XoXrQFYtezww/record");
                // Use a temporary telegramID for testing in Chrome
                const tempTelegramID = 'temp_' + Math.random().toString(36).substr(2, 9);
                const telegramID = String(tg.initDataUnsafe?.user?.id || userStore.telegramUsername || tempTelegramID);
                console.log('TelegramID before submission:', telegramID, 'Type:', typeof telegramID);
                const payload = {
                    records: [
                        {
                            fields: {
                                "First name": String(userStore.$state.firstName),
                                "Last Name": String(userStore.$state.lastName),
                                "Instagram": String(userStore.$state.instagram),
                                "About You": String(userStore.$state.about),
                                "Referral Source": String(userStore.$state.referralSource),
                                "status": "pending",
                                "telegramID": telegramID
                            }
                        }
                    ]
                };
                console.log('Payload being sent to API:', JSON.stringify(payload, null, 2));
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer teable_accwindRYobD2azy8ne_O83Or+XMAmIdRe4c5xEcWS7NDkYw9K20rF6O8+XqnbA=',
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });
                if (response.ok) {
                    const data = await response.json();
                    console.log('Teable DB response:', data);
                    router.push('/confirmation');
                }
                else {
                    const errorText = await response.text();
                    error.value = `Failed to save user data. Status: ${response.status}. Error: ${errorText}`;
                    console.error('Teable DB error:', error.value);
                }
            }
            catch (err) {
                error.value = 'An error occurred. Please try again later. ' + (err instanceof Error ? err.message : String(err));
                console.error('Error:', err);
            }
            finally {
                isSubmitting.value = false;
            }
        };
        const handleOutsideClick = (event) => {
            const target = event.target;
            if (!target.closest('input')) {
                const activeElement = document.activeElement;
                activeElement?.blur?.();
            }
        };
        return { referralSource, handleSubmit, error, isSubmitting, handleOutsideClick };
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
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("referrals") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("title") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.input, __VLS_intrinsicElements.input)({ value: ((__VLS_ctx.referralSource)), type: ("text"), placeholder: ("Referral Source"), });
    if (__VLS_ctx.error) {
        __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("error-message") }, });
        (__VLS_ctx.error);
    }
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("button-container") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleSubmit) }, ...{ class: ("primary-button") }, disabled: ((__VLS_ctx.isSubmitting)), });
    (__VLS_ctx.isSubmitting ? 'Submitting...' : 'Continue');
    __VLS_styleScopedClasses['content-wrapper'];
    __VLS_styleScopedClasses['referrals'];
    __VLS_styleScopedClasses['title'];
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