import dayjs from "dayjs";
import advancedFormat from "dayjs/plugin/advancedFormat";

// TODO: CTFd 4.0 consider removing dayjs advancedFormat
dayjs.extend(advancedFormat);

export const intl = new Intl.DateTimeFormat(
  localStorage.getItem("language") || navigator.language,
  {
    dateStyle: "long",
    timeStyle: "short",
  },
);

export default () => {
  document.querySelectorAll("[data-time]").forEach($el => {
    const time = $el.getAttribute("data-time");
    const format = $el.getAttribute("data-time-format");
    if (format) {
      $el.innerText = dayjs(time).format(format);
    } else {
      $el.innerText = intl.format(new Date(time));
    }
  });
};
