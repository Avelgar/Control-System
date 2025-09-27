// Компонент модального окна авторизации
export default {
    template: `
        <div class="modal-overlay" :class="{ active: show }" @click.self="$emit('close')">
            <div class="auth-modal">
                <button class="close-btn" @click="$emit('close')">&times;</button>
                
                <div class="auth-tabs">
                    <div class="auth-tab" :class="{ active: activeTab === 'login' }" @click="$emit('tab-change', 'login')">Вход</div>
                    <div class="auth-tab" :class="{ active: activeTab === 'register' }" @click="$emit('tab-change', 'register')">Регистрация</div>
                </div>

                <!-- Login Form -->
                <form class="auth-form" v-if="activeTab === 'login'" @submit.prevent="handleLoginSubmit">
                    <div class="form-group">
                        <label for="login-email">Email или логин</label>
                        <input type="text" id="login-email" class="form-control" v-model="loginData.username" required>
                    </div>
                    <div class="form-group">
                        <label for="login-password">Пароль</label>
                        <input type="password" id="login-password" class="form-control" v-model="loginData.password" required>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Войти</button>
                    <div class="form-footer">
                        <a href="#" @click.prevent="$emit('tab-change', 'register')">Нет аккаунта? Зарегистрируйтесь</a>
                    </div>
                </form>

                <!-- Registration Form -->
                <form class="auth-form" v-if="activeTab === 'register'" @submit.prevent="handleRegisterSubmit">
                    <div class="form-group">
                        <label for="reg-fullname">ФИО</label>
                        <input type="text" id="reg-fullname" class="form-control" v-model="registerData.fullName" required>
                    </div>
                    <div class="form-group">
                        <label for="reg-email">Email</label>
                        <input type="email" id="reg-email" class="form-control" v-model="registerData.email" required>
                    </div>
                    <div class="form-group">
                        <label for="reg-username">Логин</label>
                        <input type="text" id="reg-username" class="form-control" v-model="registerData.username" required>
                    </div>
                    <div class="form-group">
                        <label for="reg-password">Пароль</label>
                        <input type="password" id="reg-password" class="form-control" v-model="registerData.password" required>
                    </div>
                    <div class="form-group">
                        <label for="reg-confirm">Подтверждение пароля</label>
                        <input type="password" id="reg-confirm" class="form-control" v-model="registerData.confirmPassword" required>
                    </div>
                    <div class="form-group">
                        <p><small>Все новые пользователи регистрируются как наблюдатели. Роль может быть изменена администратором системы при необходимости.</small></p>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Зарегистрироваться</button>
                    <div class="form-footer">
                        <a href="#" @click.prevent="$emit('tab-change', 'login')">Уже есть аккаунт? Войдите</a>
                    </div>
                </form>
            </div>
        </div>
    `,
    props: {
        show: Boolean,
        activeTab: String
    },
    emits: ['close', 'tab-change', 'login', 'register'],
    data() {
        return {
            loginData: {
                username: '',
                password: ''
            },
            registerData: {
                fullName: '',
                email: '',
                username: '',
                password: '',
                confirmPassword: ''
            }
        };
    },
    methods: {
        handleLoginSubmit() {
            this.$emit('login', { ...this.loginData });
            this.loginData = { username: '', password: '' };
        },
        handleRegisterSubmit() {
            this.$emit('register', { ...this.registerData });
            this.registerData = { 
                fullName: '', 
                email: '', 
                username: '', 
                password: '', 
                confirmPassword: '' 
            };
        }
    },
    watch: {
        activeTab() {
            // Сброс форм при переключении вкладок
            this.loginData = { username: '', password: '' };
            this.registerData = { 
                fullName: '', 
                email: '', 
                username: '', 
                password: '', 
                confirmPassword: '' 
            };
        }
    }
};