import ModalAuth from './components/ModalAuth.js';

const { createApp } = Vue;

// Основное приложение
const app = createApp({
    components: {
        'modal-auth': ModalAuth
    },
    data() {
        return {
            showAuth: false,
            activeTab: 'login',
            loginForm: {
                username: '',
                password: ''
            },
            registerForm: {
                fullName: '',
                email: '',
                username: '',
                password: '',
                confirmPassword: ''
            }
        };
    },
    methods: {
        openModal(tab) {
            this.activeTab = tab;
            this.showAuth = true;
            document.body.style.overflow = 'hidden';
        },
        closeModal() {
            this.showAuth = false;
            document.body.style.overflow = 'auto';
        },
        handleLogin(loginData) {
            console.log('Логин:', loginData);
            // Здесь будет вызов API
            alert('Функционал входа будет реализован в бэкенде');
            this.closeModal();
        },
        handleRegister(registerData) {
            if (registerData.password !== registerData.confirmPassword) {
                alert('Пароли не совпадают');
                return;
            }
            
            console.log('Регистрация:', registerData);
            // Здесь будет вызов API
            alert('Функционал регистрации будет реализован в бэкенде');
            this.closeModal();
        }
    }
});

app.mount('#app');