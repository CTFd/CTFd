import CTFd from "@ctfdio/ctfd-js";

import dayjs from "dayjs";
import advancedFormat from "dayjs/plugin/advancedFormat";

import alerts from "./utils/alerts";
import tooltips from "./utils/tooltips";
import collapse from "./utils/collapse";

import eventAlerts from "./utils/notifications/alerts";
import eventToasts from "./utils/notifications/toasts";
import eventRead from "./utils/notifications/read";

import "./components/language";

dayjs.extend(advancedFormat);
CTFd.init(window.init);

(() => {

  alerts();
  tooltips();
  collapse();

  eventRead();
  eventAlerts();
  eventToasts();
})();

export default CTFd;
