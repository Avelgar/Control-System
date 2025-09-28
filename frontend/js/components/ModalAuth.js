const API_BASE_URL = 'http://blue.fnode.me:25526';

export default {
    template: `
        <div class="modal-overlay" :class="{ active: show }" @click.self="$emit('close')">
            <div class="auth-modal">
                <button class="close-btn" @click="$emit('close')">&times;</button>
                
                <div class="auth-tabs">
                    <div class="auth-tab" :class="{ active: activeTab === 'login' }" @click="$emit('tab-change', 'login')">Вход</div>
                    <div class="auth-tab" :class="{ active: activeTab === 'register' }" @click="$emit('tab-change', 'register')">Регистрация</div>
                </div>

                <form class="auth-form" v-if="activeTab === 'login'" @submit.prevent="handleLoginSubmit">
                    <div v-if="loginError" class="error-message">{{ loginError }}</div>
                    <div class="form-group">
                        <label for="login-username">Логин</label>
                        <input type="text" id="login-username" class="form-control" v-model="loginData.username" required>
                    </div>
                    <div class="form-group">
                        <label for="login-password">Пароль</label>
                        <input type="password" id="login-password" class="form-control" v-model="loginData.password" required>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;" :disabled="loading">
                        {{ loading ? 'Вход...' : 'Войти' }}
                    </button>
                    <div class="form-footer">
                        <a href="#" @click.prevent="$emit('tab-change', 'register')">Нет аккаунта? Зарегистрируйтесь</a>
                    </div>
                </form>

                <form class="auth-form" v-if="activeTab === 'register'" @submit.prevent="handleRegisterSubmit">
                    <div v-if="registerError" class="error-message">{{ registerError }}</div>
                    <div v-if="registerSuccess" class="success-message">{{ registerSuccess }}</div>
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
                        <p><small>Все новые пользователи регистрируются как наблюдатели. Роль может быть изменена администратором системы.</small></p>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;" :disabled="loading">
                        {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
                    </button>
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
            loginData: { username: '', password: '' },
            registerData: { fullName: '', email: '', username: '', password: '', confirmPassword: '' },
            loading: false,
            loginError: '',
            registerError: '',
            registerSuccess: ''
        };
    },
    methods: {
        async handleLoginSubmit() {
            this.loading = true;
            this.loginError = '';
            
            try {
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.loginData)
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.$emit('login', data);
                } else {
                    const error = await response.json();
                    this.loginError = error.detail || 'Ошибка входа';
                }
            } catch (error) {
                this.loginError = 'Ошибка соединения с сервером';
            } finally {
                this.loading = false;
            }
        },
        
        async handleRegisterSubmit() {
            if (this.registerData.password !== this.registerData.confirmPassword) {
                this.registerError = 'Пароли не совпадают';
                return;
            }
            
            this.loading = true;
            this.registerError = '';
            this.registerSuccess = '';
            
            try {
                const userData = {
                    username: this.registerData.username,
                    email: this.registerData.email,
                    full_name: this.registerData.fullName,
                    password: this.registerData.password
                };
                
                const response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(userData)
                });
                
                if (response.ok) {
                    this.registerSuccess = 'Регистрация успешна! Теперь вы можете войти в систему.';
                    this.registerData = { fullName: '', email: '', username: '', password: '', confirmPassword: '' };
                    setTimeout(() => {
                        this.$emit('tab-change', 'login');
                    }, 2000);
                } else {
                    const error = await response.json();
                    this.registerError = error.detail || 'Ошибка регистрации';
                }
            } catch (error) {
                this.registerError = 'Ошибка соединения с сервером';
            } finally {
                this.loading = false;
            }
        }
    },
    watch: {
        activeTab() {
            this.loginData = { username: '', password: '' };
            this.registerData = { fullName: '', email: '', username: '', password: '', confirmPassword: '' };
            this.loginError = '';
            this.registerError = '';
            this.registerSuccess = '';
        }
    }
};