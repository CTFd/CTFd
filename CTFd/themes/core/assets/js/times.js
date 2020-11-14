import dayjs from "dayjs";
import advancedFormat from "dayjs/plugin/advancedFormat";
import $ from "jquery";

dayjs.extend(advancedFormat);

export default () => {
  $("[data-time]").each((i, elem) => {
    let time = $(elem).data("time");
    elem.innerText = dayjs(time).format("MMMM Do, h:mm:ss A");
  });
};
