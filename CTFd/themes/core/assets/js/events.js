import { Howl } from "howler";
import { NativeEventSource, EventSourcePolyfill } from "event-source-polyfill";
import { ezToast, ezAlert } from "./ezq";
import {
  WindowController,
  init_notification_counter,
  inc_notification_counter,
  dec_notification_counter
} from "./utils";

const EventSource = NativeEventSource || EventSourcePolyfill;

export default root => {
  const source = new EventSource(root + "/events");
  const wc = new WindowController();
  const howl = new Howl({
    src: [
      `data:audio/webm;base64,
      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`
    ]
  });

  init_notification_counter();

  function connect() {
    source.addEventListener(
      "notification",
      function(event) {
        var data = JSON.parse(event.data);
        wc.broadcast("notification", data);
        render(data);
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
    switch (data.type) {
      case "toast": {
        inc_notification_counter();
        // Trim toast body to length
        let length = 50;
        let trimmed_content =
          data.content.length > length
            ? data.content.substring(0, length - 3) + "..."
            : data.content;
        let clicked = false;
        ezToast({
          title: data.title,
          body: trimmed_content,
          onclick: function() {
            ezAlert({
              title: data.title,
              body: data.content,
              button: "Got it!",
              success: function() {
                clicked = true;
                dec_notification_counter();
              }
            });
          },
          onclose: function() {
            if (!clicked) {
              dec_notification_counter();
            }
          }
        });
        break;
      }
      case "alert": {
        inc_notification_counter();
        ezAlert({
          title: data.title,
          body: data.content,
          button: "Got it!",
          success: function() {
            dec_notification_counter();
          }
        });
        break;
      }
      case "background": {
        inc_notification_counter();
        break;
      }
      default: {
        inc_notification_counter();
        break;
      }
    }

    if (data.sound) {
      howl.play();
    }
  }

  wc.notification = function(data) {
    render(data);
  };

  wc.masterDidChange = function() {
    if (this.isMaster) {
      connect();
    } else {
      disconnect();
    }
  };
};
