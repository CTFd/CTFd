import dayjs from "dayjs";

export const intl = new Intl.DateTimeFormat(undefined, {
  month: "long",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
  second: "numeric",
});

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
