import CTFd from "../index";
import lolight from "lolight";

export default () => {
  if (
    // default to true if config is not defined yet
    !CTFd.config.themeSettings.hasOwnProperty("use_builtin_code_highlighter") ||
    CTFd.config.themeSettings.use_builtin_code_highlighter === true
  ) {
    lolight("pre code");
  }
};
