const { createApp } = Vue;

const API_BASE_URL = 'http://blue.fnode.me:25526';

const app = createApp({
    data() {
        return {
            showRegister: false,
            isLoading: false,
            registerData: {
                fullName: '',
                email: '',
                username: '',
                password: '',
                confirmPassword: ''
            }
        };
    },
    mounted() {
        this.checkUrlMessages();
    },
    methods: {
        async handleRegisterSubmit() {
            // Валидация на клиенте
            if (!this.validateForm()) {
                return;
            }

            this.isLoading = true;

            try {
                const userData = {
                    username: this.registerData.username,
                    email: this.registerData.email,
                    full_name: this.registerData.fullName,
                    password: this.registerData.password,
                    confirm_password: this.registerData.confirmPassword
                };
                
                const response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    notificationSystem.success(
                        'Регистрация успешна! Проверьте вашу почту для подтверждения аккаунта.',
                        'Успешная регистрация',
                        8000
                    );
                    
                    this.showRegister = false;
                    this.resetForm();
                } else {
                    const error = await response.json();
                    notificationSystem.error(
                        error.detail || 'Произошла ошибка при регистрации',
                        'Ошибка регистрации'
                    );
                }
            } catch (error) {
                console.error('Registration error:', error);
                notificationSystem.error(
                    'Не удалось подключиться к серверу. Проверьте подключение к интернету.',
                    'Ошибка соединения'
                );
            } finally {
                this.isLoading = false;
            }
        },
        
        validateForm() {
            // Очистка предыдущих сообщений
            this.clearFormErrors();

            let isValid = true;

            // Проверка ФИО
            if (!this.registerData.fullName.trim()) {
                this.showFieldError('reg-fullname', 'Введите ФИО');
                isValid = false;
            } else if (this.registerData.fullName.trim().length < 2) {
                this.showFieldError('reg-fullname', 'ФИО слишком короткое');
                isValid = false;
            }

            // Проверка email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!this.registerData.email) {
                this.showFieldError('reg-email', 'Введите email');
                isValid = false;
            } else if (!emailRegex.test(this.registerData.email)) {
                this.showFieldError('reg-email', 'Введите корректный email');
                isValid = false;
            }

            // Проверка логина
            const loginRegex = /^[a-zA-Z0-9_]+$/;
            if (!this.registerData.username) {
                this.showFieldError('reg-username', 'Введите логин');
                isValid = false;
            } else if (this.registerData.username.length < 3) {
                this.showFieldError('reg-username', 'Логин должен содержать минимум 3 символа');
                isValid = false;
            } else if (!loginRegex.test(this.registerData.username)) {
                this.showFieldError('reg-username', 'Логин может содержать только латинские буквы, цифры и подчеркивание');
                isValid = false;
            }

            // Проверка пароля
            if (!this.registerData.password) {
                this.showFieldError('reg-password', 'Введите пароль');
                isValid = false;
            } else if (this.registerData.password.length < 8) {
                this.showFieldError('reg-password', 'Пароль должен содержать минимум 8 символов');
                isValid = false;
            }

            // Проверка подтверждения пароля
            if (!this.registerData.confirmPassword) {
                this.showFieldError('reg-confirm', 'Подтвердите пароль');
                isValid = false;
            } else if (this.registerData.password !== this.registerData.confirmPassword) {
                this.showFieldError('reg-confirm', 'Пароли не совпадают');
                isValid = false;
            }

            return isValid;
        },

        showFieldError(fieldId, message) {
            const field = document.getElementById(fieldId);
            if (field) {
                field.classList.add('error');
                
                // Создаем элемент ошибки
                let errorElement = field.parentNode.querySelector('.field-error');
                if (!errorElement) {
                    errorElement = document.createElement('div');
                    errorElement.className = 'field-error';
                    field.parentNode.appendChild(errorElement);
                }
                errorElement.textContent = message;
                errorElement.style.display = 'block';
            }
        },

        clearFormErrors() {
            const errors = document.querySelectorAll('.field-error');
            errors.forEach(error => error.remove());
            
            const fields = document.querySelectorAll('.form-control');
            fields.forEach(field => field.classList.remove('error'));
        },

        resetForm() {
            this.registerData = {
                fullName: '',
                email: '',
                username: '',
                password: '',
                confirmPassword: ''
            };
            this.clearFormErrors();
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