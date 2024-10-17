import { defineStore } from 'pinia';
export const useUserStore = defineStore('user', {
    state: () => ({
        firstName: '',
        lastName: '',
        instagram: '',
        linkedin: '',
        about: '',
        referralSource: ''
    }),
    actions: {
        updateUserData(data) {
            Object.assign(this, data);
        }
    }
});
//# sourceMappingURL=user.js.map