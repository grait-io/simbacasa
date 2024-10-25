import { defineStore } from 'pinia';
import tg from '../telegram';
export const useUserStore = defineStore('user', {
    state: () => ({
        firstName: '',
        lastName: '',
        instagram: '',
        linkedin: '',
        about: '',
        referralSource: '',
        telegramUsername: ''
    }),
    actions: {
        updateUserData(data) {
            Object.assign(this, data);
        },
        setTelegramUsername() {
            const user = tg.initDataUnsafe?.user;
            const chat = tg.initDataUnsafe?.chat;
            // Check chat object for username first
            if (chat && chat.username) {
                this.telegramUsername = chat.username;
                console.log('Telegram chat username set:', this.telegramUsername);
            }
            // Fallback to checking user object for username
            else if (user && user.username) {
                this.telegramUsername = user.username;
                console.log('Telegram user username set:', this.telegramUsername);
            }
            else {
                console.log('Failed to set Telegram username. Available data:', { user, chat });
            }
        }
    }
});
//# sourceMappingURL=user.js.map