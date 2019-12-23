import CTFd from "../CTFd";
import $ from "jquery";
import events from "../events";
import config from "../config";
import styles from "../styles";
import times from "../times";
import { default as helpers } from "../helpers";

CTFd.init(window.init);
window.CTFd = CTFd;
window.helpers = helpers;

$(() => {
  styles();
  times();
  events(config.urlRoot);
});
