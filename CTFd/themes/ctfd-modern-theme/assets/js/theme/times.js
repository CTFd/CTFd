import dayjs from "dayjs";
import advancedFormat from "dayjs/plugin/advancedFormat";

dayjs.extend(advancedFormat);

export default () => {
  document.querySelectorAll("[data-time]").forEach($el => {
    const time = $el.getAttribute("data-time");
    const format = $el.getAttribute("data-time-format") || "MMMM Do, h:mm:ss A";
    $el.innerText = dayjs(time).format(format);
  });
};
