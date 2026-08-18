import Alpine from "alpinejs";
import CTFd from "./index";

window.CTFd = CTFd;
window.Alpine = Alpine;

let lastId = CTFd.events.counter.read.getLast();
CTFd.fetch(`/api/v1/notifications?since_id=${lastId}`)
  .then(response => {
    return response.json();
  })
  .then(response => {
    let notifications = response.data;
    let read = CTFd.events.counter.read.getAll();
    notifications.forEach(n => {
      read.push(n.id);
    });
    CTFd.events.counter.read.setAll(read);

    CTFd.events.counter.unread.readAll();

    let count = CTFd.events.counter.unread.getAll().length;
    CTFd.events.controller.broadcast("counter", {
      count: count,
    });
    Alpine.store("unread_count", count);
  });

Alpine.start();
