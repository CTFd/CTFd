import { Howl } from "howler";
import { Notyf } from "notyf";
import { WindowController } from "./utils/windowManager";
import {
    init_notification_counter,
    inc_notification_counter,
    dec_notification_counter
} from "./utils/notificationCounter";
import { generateModal } from "./modal";

const EventSource = window.EventSource;

function sendNotification(title, body, id) {
    try {
        if (Notification.permission === "granted") {
            new Notification(title, {body, icon: window.init.smallIcon, tag: [id], requireInteraction: true});
            return true;
        }
    } catch (e) {
        console.error(e);
    }
    return false;
}

export function checkNotificationPromise() {
    try {
      Notification.requestPermission().then();
    } catch(e) {
      return false;
    }

    return true;
}

export default root => {
    const source = new EventSource(root + "/events");
    const wc = new WindowController();
    const howl = new Howl({
        src: [
            root + "/themes/luna-vite/static/sounds/notification.webm",
            root + "/themes/luna-vite/static/sounds/notification.mp3"
        ]
    });

    const notyf = new Notyf({
        duration: 0,
        dismissible: true,
        types: [{
            type: "info",
            color: false,
            backgroundColor: "#5CC9BB",
            dismissible: true,
        }]
    });

    init_notification_counter();

    function connect() {
        source.addEventListener(
            "notification",
            function (event) {
                let data = JSON.parse(event.data);
                wc.broadcast("notification", data);

                // Render in the master tab
                render(data);

                // Only play sounds in the master tab
                if (data.sound) {
                    howl.play();
                }
            },
            false
        );
    }

    function disconnect() {
        if (source) {
            source.close();
        }
    }

    function render(data) {
        // console.log("notif data", data);
        if (data.type === "toast") {
            // console.log("notif toast", data);
            inc_notification_counter();
            // Trim toast body to length
            // let length = 50;
            // let trimmed_content =
            //     data.content.length > length
            //         ? data.content.substring(0, length - 3) + "..."
            //         : data.content;
            sendNotification(data.title, data.html, data.id);
            let clicked = false;
            const toast = notyf.open({
                type: "info",
                message: `${data.title}`,
            });
            toast.on("click", () => {
                clicked = true;
                generateModal(
                    data.title,
                    data.html,
                    () => {
                        dec_notification_counter();
                    }
                );
            });
            toast.on("dismiss", () => {
                if (!clicked) {
                    dec_notification_counter();
                }
            });
        } else if (data.type === "alert") {
            inc_notification_counter();
            sendNotification(data.title, data.html, data.id);
            generateModal(
                data.title,
                data.html,
                () => {
                    dec_notification_counter();
                }
            );
        } else if (data.type === "background") {
            inc_notification_counter();
        } else {
            inc_notification_counter();
        }
    }

    wc.alert = function (data) {
        render(data);
    };
    wc.eventAlert = wc.alert;

    wc.toast = function (data) {
        render(data);
    };
    wc.eventToast = wc.toast;

    wc.background = function (data) {
        render(data);
    };
    wc.eventBackground = wc.background;

    wc.masterDidChange = function () {
        // console.log("masterDidChange", this.isMaster);
        if (this.isMaster) {
            connect();
        } else {
            disconnect();
        }
    };
};
