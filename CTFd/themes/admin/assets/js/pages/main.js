import CTFd from "core/CTFd";
import $ from "jquery";
import events from "core/events";
import times from "core/times";
import styles from "../styles";
import { default as helpers } from "core/helpers";

CTFd.init(window.init);
window.CTFd = CTFd;
window.helpers = helpers;

$(() => {
  styles();
  times();
  events(CTFd.config.urlRoot);
});
