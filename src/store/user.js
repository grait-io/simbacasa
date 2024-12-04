import { defineStore } from 'pinia';
import { ref } from 'vue';
export const useUserStore = defineStore('user', () => {
    const firstName = ref('');
    const lastName = ref('');
    const instagram = ref('');
    const linkedin = ref('');
    const referralSource = ref('');
    const telegramUsername = ref('');
    const questionsAndAnswers = ref('');
    const about = ref('');
    function updateUserData(data) {
        if (data.firstName !== undefined)
            firstName.value = data.firstName;
        if (data.lastName !== undefined)
            lastName.value = data.lastName;
        if (data.instagram !== undefined)
            instagram.value = data.instagram;
        if (data.linkedin !== undefined)
            linkedin.value = data.linkedin;
        if (data.referralSource !== undefined)
            referralSource.value = data.referralSource;
        if (data.telegramUsername !== undefined)
            telegramUsername.value = data.telegramUsername;
        if (data.questionsAndAnswers !== undefined)
            questionsAndAnswers.value = data.questionsAndAnswers;
        if (data.about !== undefined)
            about.value = data.about;
    }
    function setTelegramUsername() {
        try {
            const tg = window.Telegram?.WebApp;
            if (!tg) {
                console.log('Telegram WebApp not available');
                return;
            }
            const user = tg.initDataUnsafe?.user;
            const chat = tg.initDataUnsafe?.chat;
            if (chat?.username) {
                telegramUsername.value = chat.username;
                console.log('Telegram chat username set:', telegramUsername.value);
            }
            else if (user?.username) {
                telegramUsername.value = user.username;
                console.log('Telegram user username set:', telegramUsername.value);
            }
            else {
                console.log('Failed to set Telegram username. Available data:', { user, chat });
            }
        }
        catch (e) {
            console.error('Error setting Telegram username:', e);
        }
    }
    return {
        firstName,
        lastName,
        instagram,
        linkedin,
        referralSource,
        telegramUsername,
        questionsAndAnswers,
        about,
        updateUserData,
        setTelegramUsername
    };
});
//# sourceMappingURL=user.js.map