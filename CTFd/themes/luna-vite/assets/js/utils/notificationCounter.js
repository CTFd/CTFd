const storage = window.localStorage;
const counter_key = "unread_notifications";

function notificationBadgeOn() {
    const notificationBadgeButtons = document.querySelectorAll(".buttonNotification");
    [...notificationBadgeButtons].forEach(n => n.classList.add("buttonNotificationOn"));
}
function notificationBadgeOff() {
    const notificationBadgeButtons = document.querySelectorAll(".buttonNotification");
    [...notificationBadgeButtons].forEach(n => n.classList.remove("buttonNotificationOn"));
}

export function init_notification_counter() {
    let count = storage.getItem(counter_key);
    if (count === null) {
        storage.setItem(counter_key, 0);
    } else {
        if (count > 0) {
            // $(".badge-notification").text(count);
            notificationBadgeOn();
        }
    }
}

export function set_notification_counter(count) {
    storage.setItem(counter_key, count);
}

export function inc_notification_counter() {
    let count = storage.getItem(counter_key) || 0;
    storage.setItem(counter_key, ++count);
    // $(".badge-notification").text(count);
    notificationBadgeOn();
}

export function dec_notification_counter() {
    let count = storage.getItem(counter_key) || 0;
    if (count > 0) {
        storage.setItem(counter_key, --count);
        // $(".badge-notification").text(count);
    }
    // Always clear if count is 0
    if (count == 0) {
        clear_notification_counter();
    }
}

export function clear_notification_counter() {
    storage.setItem(counter_key, 0);
    // $(".badge-notification").empty();
    notificationBadgeOff();
}
