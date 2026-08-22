import Alpine from "alpinejs";
import CTFd from "../../index";

export default () => {
  CTFd._functions.events.eventCount = count => {
    Alpine.store("unread_count", count);
  };

  CTFd._functions.events.eventRead = eventId => {
    CTFd.events.counter.read.add(eventId);
    let count = CTFd.events.counter.unread.getAll().length;
    CTFd.events.controller.broadcast("counter", { count: count });
    Alpine.store("unread_count", count);
  };

  document.addEventListener("alpine:init", () => {
    CTFd._functions.events.eventCount(CTFd.events.counter.unread.getAll().length);
  });
};
