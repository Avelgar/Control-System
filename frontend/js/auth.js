// Модуль для работы с аутентификацией
const Auth = {
    // Роли в системе
    ROLES: {
        OBSERVER: 'observer',     // Наблюдатель (руководители/заказчики) - по умолчанию
        ENGINEER: 'engineer',     // Инженер - назначается администратором
        MANAGER: 'manager',       // Менеджер - назначается администратором
        ADMIN: 'admin'            // Администратор - системная роль
    },

    // Проверка прав доступа
    hasPermission(user, permission) {
        const permissions = {
            [this.ROLES.OBSERVER]: ['defects:read', 'reports:view'],
            [this.ROLES.ENGINEER]: ['defects:create', 'defects:read', 'defects:update-own'],
            [this.ROLES.MANAGER]: ['defects:create', 'defects:read', 'defects:update', 'projects:manage'],
            [this.ROLES.ADMIN]: ['*'] // Все права
        };

        const userPermissions = permissions[user.role] || [];
        return userPermissions.includes(permission) || userPermissions.includes('*');
    },

    // Сохранение данных пользователя
    setUser(userData) {
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('token', userData.token);
    },

    // Получение данных пользователя
    getUser() {
        const userData = localStorage.getItem('user');
        return userData ? JSON.parse(userData) : null;
    },

    // Выход из системы
    logout() {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
    }
};

export default Auth;