import Alpine from "alpinejs";
import { Modal } from "bootstrap";

import CTFd from "../../index";

export default () => {
  Alpine.store("modal", { title: "", html: "" });

  CTFd._functions.events.eventAlert = data => {
    Alpine.store("modal", data);
    let modal = new Modal(document.querySelector("[x-ref='modal']"));
    // TODO: Get rid of this private attribute access
    // See https://github.com/twbs/bootstrap/issues/31266
    modal._element.addEventListener(
      "hidden.bs.modal",
      event => {
        CTFd._functions.events.eventRead(data.id);
      },
      { once: true },
    );
    modal.show();
  };
};
