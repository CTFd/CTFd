import CTFd from "core/CTFd";
import $ from "jquery";
import events from "core/events";
import times from "core/times";
import styles from "../styles";

CTFd.init(window.init);
window.CTFd = CTFd;

$(() => {
  styles();
  times();
  events(CTFd.config.urlRoot);
});
