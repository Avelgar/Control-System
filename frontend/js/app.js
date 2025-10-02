import { API_BASE_URL } from './config.js';
import { modalMethods } from './components/modals.js';

const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            showRegister: false,
            showLogin: false,
            isLoading: false,
            userEmail: '',
            userProfile: null,
            registerData: {
                fullName: '',
                email: '',
                username: '',
                password: '',
                confirmPassword: ''
            },
            loginData: {
                login: '',
                password: ''
            }
        };
    },
    async mounted() {
        await this.checkAuthStatus();
        this.checkUrlMessages();
    },
    methods: {
        ...modalMethods,

        async checkAuthStatus() {
            const token = localStorage.getItem('authToken');
            const email = localStorage.getItem('userEmail');
            
            if (token && email) {
                try {
                    const response = await fetch(`${API_BASE_URL}/main`, {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        this.userEmail = email;
                        this.userProfile = data.user;
                        console.log('User authenticated:', data.user);
                        
                        window.location.href = '/main-page';
                    } else {
                        this.clearAuthData();
                        console.log('Token invalid, cleared auth data');
                    }
                } catch (error) {
                    console.error('Auth check error:', error);
                    this.clearAuthData();
                }
            } else if (token || email){
                this.clearAuthData();
            }
        },

        async navigateToMain() {
            const token = localStorage.getItem('authToken');
            
            if (!token) {
                notificationSystem.error('Требуется аутентификация', 'Ошибка');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/main`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    notificationSystem.success('Доступ к защищенной странице разрешен', 'Успех');
                    console.log('Main page data:', data);
                    
                } else {
                    this.clearAuthData();
                    notificationSystem.error('Сессия истекла. Войдите снова.', 'Ошибка доступа');
                }
            } catch (error) {
                console.error('Navigation error:', error);
                notificationSystem.error('Ошибка при проверке доступа', 'Ошибка');
            }
        },

        clearAuthData() {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userEmail');
            this.userEmail = '';
            this.userProfile = null;
        },

        logout() {
            this.clearAuthData();
            notificationSystem.success('Вы успешно вышли из системы', 'Выход');
        },

        checkUrlMessages() {
            const urlParams = new URLSearchParams(window.location.search);
            const success = urlParams.get('success');
            const error = urlParams.get('error');

            if (success) {
                notificationSystem.success(
                    decodeURIComponent(success),
                    'Успех',
                    8000
                );
                this.clearUrlParams();
            }

            if (error) {
                notificationSystem.error(
                    decodeURIComponent(error),
                    'Ошибка',
                    8000
                );
                this.clearUrlParams();
            }
        },

        clearUrlParams() {
            const newUrl = window.location.pathname;
            window.history.replaceState({}, document.title, newUrl);
        }
    }
});

app.mount('#app');