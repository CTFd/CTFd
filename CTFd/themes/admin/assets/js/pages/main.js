import CTFd from "core/CTFd";
import $ from "jquery";
import Moment from "moment";
import nunjucks from "nunjucks";
import { Howl } from "howler";
import events from "core/events";
import times from "core/times";
import styles from "../styles";
import { default as helpers } from "core/helpers";

CTFd.init(window.init);
window.CTFd = CTFd;
window.helpers = helpers;
window.$ = $;
window.Moment = Moment;
window.nunjucks = nunjucks;
window.Howl = Howl;

$(() => {
  styles();
  times();
  events(CTFd.config.urlRoot);
});
