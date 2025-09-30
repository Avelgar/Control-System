// notifications.js

class NotificationSystem {
    constructor() {
        this.container = null;
        this.notifications = new Set();
        this.init();
    }

    init() {
        // Создаем контейнер для уведомлений
        this.container = document.createElement('div');
        this.container.className = 'notification-container';
        document.body.appendChild(this.container);
    }

    show(message, type = 'info', title = null, duration = 5000) {
        const notification = this.createNotification(message, type, title, duration);
        this.container.appendChild(notification.element);
        this.notifications.add(notification);

        // Автоматическое закрытие
        if (duration > 0) {
            notification.timeout = setTimeout(() => {
                this.close(notification);
            }, duration);
        }

        return notification;
    }

    createNotification(message, type, title, duration) {
        const notification = {
            id: Date.now() + Math.random(),
            element: null,
            timeout: null
        };

        const notificationEl = document.createElement('div');
        notificationEl.className = `notification ${type}`;
        notificationEl.innerHTML = `
            <div class="notification-header">
                <div class="notification-title">${title || this.getDefaultTitle(type)}</div>
                <button class="notification-close" onclick="notificationSystem.closeById(${notification.id})">&times;</button>
            </div>
            <div class="notification-message">${message}</div>
            ${duration > 0 ? '<div class="notification-progress"></div>' : ''}
        `;

        notification.element = notificationEl;
        return notification;
    }

    getDefaultTitle(type) {
        const titles = {
            success: 'Успех',
            error: 'Ошибка',
            warning: 'Предупреждение',
            info: 'Информация'
        };
        return titles[type] || 'Уведомление';
    }

    close(notification) {
        if (notification.timeout) {
            clearTimeout(notification.timeout);
        }

        notification.element.classList.add('fade-out');
        
        setTimeout(() => {
            if (notification.element.parentNode) {
                notification.element.parentNode.removeChild(notification.element);
            }
            this.notifications.delete(notification);
        }, 300);
    }

    closeById(id) {
        for (const notification of this.notifications) {
            if (notification.id === id) {
                this.close(notification);
                break;
            }
        }
    }

    closeAll() {
        this.notifications.forEach(notification => {
            this.close(notification);
        });
    }

    success(message, title = null, duration = 5000) {
        return this.show(message, 'success', title, duration);
    }

    error(message, title = null, duration = 7000) {
        return this.show(message, 'error', title, duration);
    }

    warning(message, title = null, duration = 6000) {
        return this.show(message, 'warning', title, duration);
    }

    info(message, title = null, duration = 5000) {
        return this.show(message, 'info', title, duration);
    }
}

// Создаем глобальный экземпляр
const notificationSystem = new NotificationSystem();

// Экспорт для использования в модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = notificationSystem;
} else {
    window.notificationSystem = notificationSystem;
}