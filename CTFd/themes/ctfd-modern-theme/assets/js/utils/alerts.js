import { Alert } from "bootstrap";

export default () => {
  const alertList = [].slice.call(document.querySelectorAll(".alert"));
  alertList.map(function (element) {
    return new Alert(element);
  });
};
