import { clear_notification_counter } from "./utils/notificationCounter";

(() => {
    clear_notification_counter();
    if (Notification.permission === "default") {
        Notification.requestPermission();
    }
})();
