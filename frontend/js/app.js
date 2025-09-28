import ModalAuth from './components/ModalAuth.js';

const { createApp } = Vue;

const app = createApp({
    components: {
        'modal-auth': ModalAuth
    },
    data() {
        return {
            showAuth: false,
            activeTab: 'login',
            currentUser: null
        };
    },
    mounted() {
        this.checkAuthStatus();
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
        async handleLogin(data) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            this.currentUser = data.user;
            this.closeModal();
        },
        async checkAuthStatus() {
            const token = localStorage.getItem('token');
            const user = localStorage.getItem('user');
            
            if (token && user) {
                try {
                    const response = await fetch('http://blue.fnode.me:25526/users/me', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    
                    if (response.ok) {
                        this.currentUser = JSON.parse(user);
                    } else {
                        this.logout();
                    }
                } catch (error) {
                    this.logout();
                }
            }
        },
        logout() {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            this.currentUser = null;
        },
        getRoleName(role) {
            const roleNames = {
                'observer': 'Наблюдатель',
                'engineer': 'Инженер',
                'manager': 'Менеджер',
                'admin': 'Администратор'
            };
            return roleNames[role] || role;
        }
    }
});

app.mount('#app');