import $ from "jquery";
import events from "../compat/events";
import CTFd from "core/CTFd";

$(() => {
  events(CTFd.config.urlRoot);
});
