import { Howl } from "howler";
import { NativeEventSource, EventSourcePolyfill } from "event-source-polyfill";
import { ezAlert, ezToast } from "./ezq";
import { WindowController } from "./utils";

const EventSource = NativeEventSource || EventSourcePolyfill;

export default root => {
  const source = new EventSource(root + "/events");
  const wc = new WindowController();
  const howl = new Howl({
    src: [
      root + "/themes/core/static/sounds/notification.webm",
      root + "/themes/core/static/sounds/notification.mp3"
    ]
  });

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
    ezToast({
      title: data.title,
      body: data.content
    });
    howl.play();
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
