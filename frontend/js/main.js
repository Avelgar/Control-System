const { createApp } = Vue;
import { API_BASE_URL } from './config.js';

createApp({
    data() {
        return {
            isLoading: true,
            userProfile: null,
            error: null,
            // Данные для всех ролей
            projects: [],
            defects: [],
            myDefects: [],
            stats: {},
            // Флаги для модальных окон
            showCreateProject: false,
            showCreateDefect: false,
            showAllDefects: false
        };
    },
    async mounted() {
        await this.checkAuthentication();
        if (this.userProfile) {
            await this.loadInitialData();
        }
    },
    methods: {
        async checkAuthentication() {
            const token = localStorage.getItem('authToken');
            const email = localStorage.getItem('userEmail');
            
            if (!token || !email) {
                this.redirectToLogin();
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
                    this.userProfile = data.user;
                    this.isLoading = false;
                } else {
                    this.clearAuthData();
                    this.redirectToLogin();
                }
            } catch (error) {
                console.error('Auth check error:', error);
                this.clearAuthData();
                this.redirectToLogin();
            }
        },

        async loadInitialData() {
            try {
                await this.loadProjects();
                await this.loadDefects();
                await this.loadStatistics();
                
                // Для инженера фильтруем его дефекты
                if (this.userProfile.role === 'engineer') {
                    this.myDefects = this.defects.filter(defect => 
                        defect.reported_by === this.userProfile.id
                    );
                }
            } catch (error) {
                console.error('Error loading initial data:', error);
                this.showNotification('Ошибка загрузки данных', 'error');
            }
        },

        async loadProjects() {
            try {
                const token = localStorage.getItem('authToken');
                const response = await fetch(`${API_BASE_URL}/api/projects`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (response.ok) {
                    this.projects = await response.json();
                } else {
                    console.error('Failed to load projects');
                }
            } catch (error) {
                console.error('Error loading projects:', error);
            }
        },

        async loadDefects() {
            try {
                const token = localStorage.getItem('authToken');
                const response = await fetch(`${API_BASE_URL}/api/defects`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    this.defects = await response.json();
                } else {
                    console.error('Failed to load defects');
                }
            } catch (error) {
                console.error('Error loading defects:', error);
            }
        },

        async loadAllDefects() {
            await this.loadDefects();
            this.showAllDefects = true;
        },

        async loadStatistics() {
            try {
                const token = localStorage.getItem('authToken');
                const response = await fetch(`${API_BASE_URL}/api/reports/defects-statistics`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    this.stats = await response.json();
                } else {
                    console.error('Failed to load statistics');
                }
            } catch (error) {
                console.error('Error loading statistics:', error);
            }
        },

        async loadMyDefects() {
            if (this.userProfile.role === 'engineer') {
                this.myDefects = this.defects.filter(defect => 
                    defect.reported_by === this.userProfile.id
                );
                this.showAllDefects = true;
            }
        },

        async loadUsers() {
            if (this.userProfile.role !== 'manager') {
                this.showNotification('Недостаточно прав', 'error');
                return;
            }

            try {
                const token = localStorage.getItem('authToken');
                const response = await fetch(`${API_BASE_URL}/api/users`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const users = await response.json();
                    this.showNotification(`Загружено ${users.length} пользователей`, 'info');
                }
            } catch (error) {
                console.error('Error loading users:', error);
                this.showNotification('Ошибка загрузки пользователей', 'error');
            }
        },

        async generateReport() {
            try {
                this.showNotification('Отчёт формируется...', 'info');
                
                // Временная заглушка
                setTimeout(() => {
                    this.showNotification('Отчёт успешно сформирован', 'success');
                }, 2000);
                
            } catch (error) {
                console.error('Error generating report:', error);
                this.showNotification('Ошибка формирования отчёта', 'error');
            }
        },

        getRoleName(role) {
            const roles = {
                'manager': 'Менеджер',
                'engineer': 'Инженер', 
                'observer': 'Наблюдатель'
            };
            return roles[role] || role;
        },

        getProjectDefectsCount(projectId) {
            return this.defects.filter(defect => defect.project_id === projectId).length;
        },

        getProjectCompletedCount(projectId) {
            return this.defects.filter(defect => 
                defect.project_id === projectId && defect.status === 'закрыта'
            ).length;
        },

        getProjectProgress(projectId) {
            const total = this.getProjectDefectsCount(projectId);
            const completed = this.getProjectCompletedCount(projectId);
            return total > 0 ? Math.round((completed / total) * 100) : 0;
        },

        getMyDefectsCount() {
            return this.myDefects.length;
        },

        getDefectsByStatus(status) {
            return this.myDefects.filter(defect => defect.status === status).length;
        },

        formatDate(dateString) {
            if (!dateString) return 'Не указан';
            return new Date(dateString).toLocaleDateString('ru-RU');
        },

        viewProject(projectId) {
            this.showNotification(`Просмотр проекта ID: ${projectId}`, 'info');
        },

        async updateDefectStatus(defectId) {
            try {
                this.showNotification('Обновление статуса дефекта', 'info');
            } catch (error) {
                console.error('Error updating defect:', error);
                this.showNotification('Ошибка обновления дефекта', 'error');
            }
        },

        showNotification(message, type = 'info') {
            // Простая замена notificationSystem
            const styles = {
                success: 'background: #27ae60; color: white; padding: 10px;',
                error: 'background: #e74c3c; color: white; padding: 10px;',
                info: 'background: #3498db; color: white; padding: 10px;',
                warning: 'background: #f39c12; color: white; padding: 10px;'
            };
            console.log(`%c${message}`, styles[type] || styles.info);
        },
        
        clearAuthData() {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userEmail');
        },
        
        redirectToLogin() {
            window.location.href = '/';
        },
        
        logout() {
            this.clearAuthData();
            window.location.href = '/';
        }
    }
}).mount('#main-app');