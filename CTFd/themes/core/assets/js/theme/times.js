import dayjs from "dayjs";
import advancedFormat from "dayjs/plugin/advancedFormat";

// TODO: CTFd 4.0 consider removing dayjs advancedFormat
dayjs.extend(advancedFormat);

function getIntl() {
  // According to BCP47 underscores are not supported
  const lang =
    localStorage.getItem("language")?.replace(/_/g, "-") || navigator.language;
  const options = {
    dateStyle: "long",
    timeStyle: "short",
  };
  try {
    return new Intl.DateTimeFormat(lang, options);
  } catch (error) {
    if (error instanceof RangeError) {
      return new Intl.DateTimeFormat(undefined, options);
    }
    throw error;
  }
}
export const intl = getIntl();

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
