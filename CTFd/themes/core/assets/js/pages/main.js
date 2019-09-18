import CTFd from "../CTFd";
import $ from "jquery";
import events from "../events";
import config from "../config";
import styles from "../styles";
import times from "../times";

CTFd.init(window.init);
window.CTFd = CTFd;

$(() => {
  styles();
  times();
  events(config.urlRoot);
});
