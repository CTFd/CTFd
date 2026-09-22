import CTFd from "../index";
import lolight from "lolight";

export default () => {
  if (
    !CTFd.config.themeSettings.hasOwnProperty("use_builtin_code_highlighter") ||
    CTFd.config.themeSettings.use_builtin_code_highlighter === true
  ) {
    lolight("pre code");
  }
};
