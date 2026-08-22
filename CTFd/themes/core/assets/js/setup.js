import Alpine from "alpinejs";
import dayjs from "dayjs";
import { Tab } from "bootstrap";

import CTFd from "./index";

window.Alpine = Alpine;

Alpine.data("SetupForm", () => ({
  init() {
    // Bind Enter on any input to clicking the Next button
    this.$root.querySelectorAll("input").forEach(i => {
      i.addEventListener("keypress", e => {
        if (e.key == "Enter") {
          e.preventDefault();
          e.target.closest(".tab-pane").querySelector("button[data-href]").click();
        }
      });
      i.addEventListener("change", e => {
        if (e.target.checkValidity() === false) {
          e.target.classList.add("input-filled-invalid");
        } else {
          e.target.classList.remove("input-filled-invalid");
        }
      });
    });

    // Register storage listener for MLC integration
    window.addEventListener("storage", function (event) {
      if (event.key == "integrations" && event.newValue) {
        let integration = JSON.parse(event.newValue);
        if (integration["name"] == "mlc") {
          $("#integration-mlc").text("Already Configured").attr("disabled", true);
          window.focus();
          localStorage.removeItem("integrations");
        }
      }
    });
  },

  validateFileSize(e, limit) {
    if (e.target.files[0].size > limit) {
      if (
        !confirm(
          `This image file is larger than ${
            limit / 1000
          }KB which may result in increased load times. Are you sure you'd like to use this file?`,
        )
      ) {
        e.target.value = "";
      }
    }
  },

  switchTab(e) {
    // Handle tab validation
    let valid_tab = true;
    let inputs = e.target
      .closest('[role="tabpanel"]')
      .querySelectorAll("input,textarea");

    inputs.forEach(e => {
      if (e.checkValidity() === false) {
        e.classList.add("input-filled-invalid");
        valid_tab = false;
      }
    });

    if (valid_tab == false) {
      return;
    }

    let target = e.target.dataset.href;
    let tab = this.$root.querySelector(`[data-bs-target="${target}"]`);
    Tab.getOrCreateInstance(tab).show();
  },

  setThemeColor(e) {
    document.querySelector("#config-color-input").value = e.target.value;
  },

  resetThemeColor(_e) {
    document.querySelector("#config-color-input").value = "";
    document.querySelector("#config-color-picker").value = "";
  },

  processDateTime(datetime) {
    return function (_event) {
      let date_picker = document.querySelector(`#${datetime}-date`);
      let time_picker = document.querySelector(`#${datetime}-time`);
      let unix_time = dayjs(
        `${date_picker.value} ${time_picker.value}`,
        "YYYY-MM-DD HH:mm",
      ).unix();

      if (isNaN(unix_time)) {
        document.querySelector(`#${datetime}-preview`).value = "";
      } else {
        document.querySelector(`#${datetime}-preview`).value = unix_time;
      }
    };
  },

  mlcSetup() {
    let r = CTFd.config.urlRoot;
    let params = {
      name: document.querySelector("#ctf_name").value,
      type: "jeopardy",
      description: document.querySelector("#ctf_description").value,
      user_mode: document.querySelector("[name=user_mode]:checked").value,
      event_url: window.location.origin + r,
      redirect_url: window.location.origin + r + "/redirect",
      integration_setup_url: window.location.origin + r + "/setup/integrations",
      start: document.querySelector("#start-preview").value,
      end: document.querySelector("#end-preview").value,
      platform: "CTFd",
      state: window.STATE,
    };

    const ret = [];
    for (let p in params) {
      ret.push(encodeURIComponent(p) + "=" + encodeURIComponent(params[p]));
    }
    window.open(
      "https://www.majorleaguecyber.org/events/new?" + ret.join("&"),
      "_blank",
    );
  },

  submitSetup(e) {
    if (document.querySelector("#newsletter-checkbox").checked) {
      let email = e.target.querySelector("input[name=email]").value;
      let params = {
        email: email,
        b_38e27f7d496889133d2214208_d7c3ed71f9: "",
        c: "jsonp_callback_" + Math.round(10000 * Math.random()),
      };
      const ret = [];
      for (let p in params) {
        ret.push(encodeURIComponent(p) + "=" + encodeURIComponent(params[p]));
      }

      var script = document.createElement("script");
      script.src =
        "https://newsletters.ctfd.io/lists/ot889gr1sa0e1/subscribe/post-json?" +
        ret.join("&");
      document.head.appendChild(script);
    }
  },
}));

Alpine.start();
