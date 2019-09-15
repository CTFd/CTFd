import $ from "jquery";
import events from "core/events";
import CTFd from "core/CTFd";

$(() => {
  events(CTFd.config.urlRoot);
});
