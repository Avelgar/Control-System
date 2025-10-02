import { API_BASE_URL } from '../config.js';

export const modalMethods = {
    openModal(modalType) {
        if (modalType === 'login') {
            this.showLogin = true;
        } else if (modalType === 'register') {
            this.showRegister = true;
        }
        this.disableScroll();
    },
    
    closeModals() {
        this.showLogin = false;
        this.showRegister = false;
        this.enableScroll();
    },

    disableScroll() {
        document.body.classList.add('modal-open');
    },

    enableScroll() {
        document.body.classList.remove('modal-open');
    },

    async handleLoginSubmit() {
        if (!this.validateLoginForm()) {
            return;
        }
        
        this.isLoading = true;

        try {
            const userData = {
                login: this.loginData.login,
                password: this.loginData.password
            };
            
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });
            
            if (response.ok) {
                const data = await response.json();
                
                notificationSystem.success(
                    'Вход прошёл успешно!',
                    'Успешный вход',
                    3000
                );
                
                this.closeModals();
                this.resetForm();
                
                const tokenPayload = JSON.parse(atob(data.access_token.split('.')[1]));
                const userEmail = tokenPayload.email;
                
                localStorage.setItem('authToken', data.access_token);
                localStorage.setItem('userEmail', userEmail);
                
                console.log('User email saved:', userEmail);
                
                setTimeout(() => {
                    window.location.href = '/main-page';
                }, 1000);
                
            } else {
                const error = await response.json();
                notificationSystem.error(
                    error.detail || 'Произошла ошибка при входе',
                    'Ошибка входа'
                );
            }
        } catch (error) {
            console.error('Login error:', error);
            notificationSystem.error(
                'Не удалось подключиться к серверу. Проверьте подключение к интернету.',
                'Ошибка соединения'
            );
        } finally {
            this.isLoading = false;
        }
    },

    async handleRegisterSubmit() {
        if (!this.validateRegisterForm()) {
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
                
                this.closeModals();
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

    validateRegisterForm() {
        this.clearFormErrors();

        let isValid = true;

        if (!this.registerData.fullName.trim()) {
            this.showFieldError('reg-fullname', 'Введите ФИО');
            isValid = false;
        } else if (this.registerData.fullName.trim().length < 2) {
            this.showFieldError('reg-fullname', 'ФИО слишком короткое');
            isValid = false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!this.registerData.email) {
            this.showFieldError('reg-email', 'Введите email');
            isValid = false;
        } else if (!emailRegex.test(this.registerData.email)) {
            this.showFieldError('reg-email', 'Введите корректный email');
            isValid = false;
        }

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

        if (!this.registerData.password) {
            this.showFieldError('reg-password', 'Введите пароль');
            isValid = false;
        } else if (this.registerData.password.length < 8) {
            this.showFieldError('reg-password', 'Пароль должен содержать минимум 8 символов');
            isValid = false;
        }

        if (!this.registerData.confirmPassword) {
            this.showFieldError('reg-confirm', 'Подтвердите пароль');
            isValid = false;
        } else if (this.registerData.password !== this.registerData.confirmPassword) {
            this.showFieldError('reg-confirm', 'Пароли не совпадают');
            isValid = false;
        }

        return isValid;
    },

    validateLoginForm() {
        this.clearFormErrors();

        let isValid = true;

        if (!this.loginData.login) {
            this.showFieldError('log-login', 'Введите логин или email'); 
            isValid = false;
        } else if (this.loginData.login.length < 3) {
            this.showFieldError('log-login', 'Логин должен содержать минимум 3 символа');
            isValid = false;
        }
        
        if (!this.loginData.password) {
            this.showFieldError('log-password', 'Введите пароль');
            isValid = false;
        } else if (this.loginData.password.length < 8) {
            this.showFieldError('log-password', 'Пароль должен содержать минимум 8 символов');
            isValid = false;
        }
        
        return isValid;
    },

    resetForm() {
        this.registerData = {
            fullName: '',
            email: '',
            username: '',
            password: '',
            confirmPassword: ''
        };
        this.loginData = {	
            login: '',
            password: ''
        };
        this.clearFormErrors();
    },

    showFieldError(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.classList.add('error');
            
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
    }
};