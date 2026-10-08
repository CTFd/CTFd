import dayjs from "dayjs";
import advancedFormat from "dayjs/plugin/advancedFormat";

// TODO: CTFd 4.0 consider removing dayjs advancedFormat
dayjs.extend(advancedFormat);

const dateTimeOptions = {
  dateStyle: "long",
  timeStyle: "short",
};

function createIntl() {
  // CTFd's server-side locale identifiers use underscores, while Intl uses
  // BCP47 language tags with hyphens (for example, zh_CN -> zh-CN).
  const storedLanguage = localStorage.getItem("language");
  const language = storedLanguage?.replace(/_/g, "-");

  try {
    return new Intl.DateTimeFormat(language || navigator.language, dateTimeOptions);
  } catch (error) {
    if (!(error instanceof RangeError)) {
      throw error;
    }

    // A stale or otherwise invalid localStorage value must not stop the core
    // theme from initializing. Let Intl use the browser's default locale.
    return new Intl.DateTimeFormat(undefined, dateTimeOptions);
  }
}

export const intl = createIntl();

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
