import { defineStore } from 'pinia';

interface UserState {
  firstName: string;
  lastName: string;
  instagram: string;
  linkedin: string;
  referralSource: string;
  telegramUsername: string;
  questionsAndAnswers: string;
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    firstName: '',
    lastName: '',
    instagram: '',
    linkedin: '',
    referralSource: '',
    telegramUsername: '',
    questionsAndAnswers: ''
  }),
  actions: {
    updateUserData(data: Partial<UserState>) {
      Object.assign(this.$state, data);
    },
    setTelegramUsername() {
      try {
        const tg = (window as any).Telegram?.WebApp;
        if (!tg) {
          console.log('Telegram WebApp not available');
          return;
        }

        const user = tg.initDataUnsafe?.user;
        const chat = tg.initDataUnsafe?.chat;

        // Check chat object for username first
        if (chat?.username) {
          this.telegramUsername = chat.username;
          console.log('Telegram chat username set:', this.telegramUsername);
        }
        // Fallback to checking user object for username
        else if (user?.username) {
          this.telegramUsername = user.username;
          console.log('Telegram user username set:', this.telegramUsername);
        } else {
          console.log('Failed to set Telegram username. Available data:', { user, chat });
        }
      } catch (e) {
        console.error('Error setting Telegram username:', e);
      }
    }
  }
});
