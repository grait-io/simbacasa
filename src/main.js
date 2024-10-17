import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import { createPinia } from 'pinia';
import App from './App.vue';
import Welcome from './components/Welcome.vue';
import Name from './components/Name.vue';
import Socials from './components/Socials.vue';
import AboutYou from './components/AboutYou.vue';
import Referrals from './components/Referrals.vue';
import Confirmation from './components/Confirmation.vue';
const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', component: Welcome },
        { path: '/name', component: Name },
        { path: '/socials', component: Socials },
        { path: '/about-you', component: AboutYou },
        { path: '/referrals', component: Referrals },
        { path: '/confirmation', component: Confirmation },
    ]
});
const pinia = createPinia();
createApp(App).use(router).use(pinia).mount('#app');
//# sourceMappingURL=main.js.map