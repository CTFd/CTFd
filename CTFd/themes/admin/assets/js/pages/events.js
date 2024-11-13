import $ from "jquery";
import events from "../compat/events";
import CTFd from "../../compat/CTFd";

$(() => {
  events(CTFd.config.urlRoot);
});
