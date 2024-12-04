import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../store/user';
export default defineComponent({
    name: 'Questions',
    setup() {
        const router = useRouter();
        const userStore = useUserStore();
        const questions = ref([]);
        const answers = ref([]);
        const loading = ref(true);
        const error = ref('');
        const isSubmitting = ref(false);
        const questionsContainer = ref(null);
        const canSubmit = computed(() => {
            return answers.value.every(answer => answer && answer.trim().length > 0);
        });
        const fetchQuestions = async () => {
            try {
                const url = new URL("https://teable.grait.io/api/table/tbl1tcysT4sGwT5jmTz/record");
                const response = await fetch(url, {
                    method: "GET",
                    headers: {
                        "Authorization": "Bearer teable_accwindRYobD2azy8ne_O83Or+XMAmIdRe4c5xEcWS7NDkYw9K20rF6O8+XqnbA=",
                        "Accept": "application/json"
                    }
                });
                if (!response.ok) {
                    throw new Error(`Failed to fetch questions: ${response.status}`);
                }
                const data = await response.json();
                questions.value = data.records.filter((record) => record.fields && record.fields.question);
                answers.value = new Array(questions.value.length).fill('');
                console.log('Fetched questions:', questions.value);
            }
            catch (err) {
                error.value = 'Failed to load questions. Please try again later.';
                console.error('Error fetching questions:', err);
            }
            finally {
                loading.value = false;
            }
        };
        const handleSubmit = async () => {
            if (!canSubmit.value)
                return;
            isSubmitting.value = true;
            window.scrollTo({ top: 0, behavior: 'smooth' });
            // Format questions and answers as a single string
            const formattedAnswers = questions.value
                .map((q, index) => `${q.fields.question}\n${answers.value[index]}`)
                .join('\n\n');
            console.log('Formatted answers:', formattedAnswers);
            // Store the formatted string directly
            userStore.$state.questionsAndAnswers = formattedAnswers;
            console.log('Updated user store:', userStore.$state);
            // Navigate to referrals page
            router.push('/referrals');
            isSubmitting.value = false;
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
        onMounted(() => {
            fetchQuestions();
        });
        return {
            questions,
            answers,
            loading,
            error,
            isSubmitting,
            canSubmit,
            handleSubmit,
            handleBack,
            handleOutsideClick,
            questionsContainer
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
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleBack) }, ...{ class: ("back-button") }, "aria-label": ("Go back"), });
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("questions") }, ref: ("questionsContainer"), });
    // @ts-ignore navigation for `const questionsContainer = ref()`
    __VLS_ctx.questionsContainer;
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleBack) }, ...{ class: ("back-button") }, "aria-label": ("Go back"), });
    __VLS_elementAsFunction(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({ ...{ class: ("arrow") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_elementAsFunction(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    if (__VLS_ctx.loading) {
        __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("loading") }, });
    }
    else if (__VLS_ctx.error) {
        __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("error-message") }, });
        (__VLS_ctx.error);
    }
    else {
        __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("questions-list") }, });
        for (const [question, index] of __VLS_getVForSourceType((__VLS_ctx.questions))) {
            __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ key: ((question.id)), ...{ class: ("question-item") }, });
            __VLS_elementAsFunction(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({ ...{ class: ("grey") }, });
            (question.fields.question);
            __VLS_elementAsFunction(__VLS_intrinsicElements.textarea, __VLS_intrinsicElements.textarea)({ value: ((__VLS_ctx.answers[index])), placeholder: (('Your answer...')), rows: ("3"), });
        }
    }
    __VLS_elementAsFunction(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({ ...{ class: ("button-container") }, });
    __VLS_elementAsFunction(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({ ...{ onClick: (__VLS_ctx.handleSubmit) }, ...{ class: ("primary-button") }, disabled: ((__VLS_ctx.isSubmitting || !__VLS_ctx.canSubmit)), });
    (__VLS_ctx.isSubmitting ? 'Submitting...' : 'Continue');
    __VLS_styleScopedClasses['content-wrapper'];
    __VLS_styleScopedClasses['back-button'];
    __VLS_styleScopedClasses['questions'];
    __VLS_styleScopedClasses['back-button'];
    __VLS_styleScopedClasses['arrow'];
    __VLS_styleScopedClasses['loading'];
    __VLS_styleScopedClasses['error-message'];
    __VLS_styleScopedClasses['questions-list'];
    __VLS_styleScopedClasses['question-item'];
    __VLS_styleScopedClasses['grey'];
    __VLS_styleScopedClasses['button-container'];
    __VLS_styleScopedClasses['primary-button'];
    var __VLS_slots;
    var __VLS_inheritedAttrs;
    const __VLS_refs = {
        "questionsContainer": __VLS_nativeElements['div'],
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
//# sourceMappingURL=Questions.vue.js.map