import Alpine from "alpinejs";
import dayjs from "dayjs";
import { Tab } from "bootstrap";

import CTFd from "./index";

window.Alpine = Alpine;

Alpine.data("SetupForm", () => ({
  git: {
    providers: window.GIT_PROVIDERS || {},
    selecting: null,
    provider: null,
    user: null,
    device: null,
    pat: "",
    repos: [],
    selectedRepo: "",
    mode: "select",
    newRepoName: "",
    newRepoPrivate: true,
    repo: null,
    busy: false,
    error: null,
  },
  devicePollTimer: null,

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
  },

  async gitRequest(method, url, body) {
    const options = { method };
    if (body !== undefined) {
      options.body = JSON.stringify(body);
    }

    const response = await CTFd.fetch(url, options);
    let data = {};
    try {
      data = await response.json();
    } catch (_e) {
      // fallthrough to the generic error below
    }

    if (!response.ok || data.success === false) {
      throw new Error(
        (data.errors && data.errors[0]) || "Request failed, please try again",
      );
    }

    return data.data;
  },

  selectGitProvider(provider) {
    this.git.selecting = provider;
    this.git.error = null;
    this.git.pat = "";
  },

  cancelGitConnect() {
    clearTimeout(this.devicePollTimer);
    this.git.selecting = null;
    this.git.device = null;
    this.git.error = null;
    this.git.pat = "";
  },

  async startDeviceLogin(provider) {
    this.git.error = null;
    this.git.busy = true;
    try {
      const data = await this.gitRequest("POST", `/setup/git/${provider}/device`);
      this.git.device = data;
      this.pollDeviceLogin(provider, (data.interval || 5) * 1000);
    } catch (e) {
      this.git.error = e.message;
    } finally {
      this.git.busy = false;
    }
  },

  pollDeviceLogin(provider, interval) {
    this.devicePollTimer = setTimeout(async () => {
      try {
        const data = await this.gitRequest(
          "POST",
          `/setup/git/${provider}/device/token`,
        );
        if (data.status === "ok") {
          this.git.device = null;
          await this.gitConnected(provider, data.user);
        } else {
          this.pollDeviceLogin(provider, interval);
        }
      } catch (e) {
        this.git.device = null;
        this.git.error = e.message;
      }
    }, interval);
  },

  async tokenLogin(provider) {
    this.git.error = null;
    this.git.busy = true;
    try {
      const data = await this.gitRequest("POST", `/setup/git/${provider}/token`, {
        token: this.git.pat,
      });
      await this.gitConnected(provider, data.user);
    } catch (e) {
      this.git.error = e.message;
    } finally {
      this.git.busy = false;
    }
  },

  async gitConnected(provider, user) {
    this.git.selecting = null;
    this.git.provider = provider;
    this.git.user = user;
    this.git.pat = "";
    try {
      this.git.repos = await this.gitRequest(
        "GET",
        `/setup/git/${provider}/repositories`,
      );
    } catch (e) {
      this.git.error = e.message;
    }
  },

  async submitRepository(body) {
    this.git.error = null;
    this.git.busy = true;
    try {
      const data = await this.gitRequest(
        "POST",
        `/setup/git/${this.git.provider}/repositories`,
        body,
      );
      this.git.repo = data.repository;
    } catch (e) {
      this.git.error = e.message;
    } finally {
      this.git.busy = false;
    }
  },

  async linkRepository() {
    const repo = this.git.repos.find(
      r => String(r.id) === String(this.git.selectedRepo),
    );
    if (repo) {
      await this.submitRepository({ action: "select", repository: repo });
    }
  },

  async createRepository() {
    await this.submitRepository({
      action: "create",
      name: this.git.newRepoName,
      private: this.git.newRepoPrivate,
    });
  },

  unlinkRepository() {
    this.git.repo = null;
  },

  async disconnectGit() {
    clearTimeout(this.devicePollTimer);
    try {
      await this.gitRequest("DELETE", "/setup/git");
    } catch (_e) {
      // Clearing a session that does not exist is fine
    }
    this.git.provider = null;
    this.git.user = null;
    this.git.repos = [];
    this.git.selectedRepo = "";
    this.git.repo = null;
    this.git.device = null;
    this.git.error = null;
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
