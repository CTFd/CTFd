import Alpine from "alpinejs";
import { Modal } from "bootstrap";
import { serializeJSON } from "@ctfdio/ctfd-js/forms";

import CTFd from "./index";
import { copyToClipboard } from "./utils/clipboard";

window.Alpine = Alpine;

Alpine.data("SettingsForm", () => ({
  success: null,
  error: null,
  initial: null,
  errors: [],

  init() {
    this.initial = serializeJSON(this.$el);
  },

  async updateProfile() {
    this.success = null;
    this.error = null;
    this.errors = [];

    let data = serializeJSON(this.$el, this.initial, true);

    // Process fields[id] to fields: {}
    data.fields = [];
    for (const property in data) {
      if (property.match(/fields\[\d+\]/)) {
        let field = {};
        let id = parseInt(property.slice(7, -1));
        field["field_id"] = id;
        field["value"] = data[property];
        data.fields.push(field);
        delete data[property];
      }
    }

    // Send API request
    const response = await CTFd.pages.settings.updateSettings(data);
    if (response.success) {
      this.success = true;
      this.error = false;

      setTimeout(() => {
        this.success = null;
        this.error = null;
      }, 3000);
    } else {
      this.success = false;
      this.error = true;

      Object.keys(response.errors).map(error => {
        const error_msg = response.errors[error];
        this.errors.push(error_msg);
      });
    }
  },
}));

Alpine.data("TokensForm", () => ({
  token: null,

  async generateToken() {
    const data = serializeJSON(this.$el);

    if (!data.expiration) {
      delete data.expiration;
    }
    const response = await CTFd.pages.settings.generateToken(data);
    this.token = response.data.value;

    new Modal(this.$refs.tokenModal).show();
  },

  copyToken() {
    copyToClipboard(this.$refs.token);
  },
}));

Alpine.data("Tokens", () => ({
  selectedTokenId: null,

  async deleteTokenModal(tokenId) {
    this.selectedTokenId = tokenId;
    new Modal(this.$refs.confirmModal).show();
  },

  async deleteSelectedToken() {
    await CTFd.pages.settings.deleteToken(this.selectedTokenId);
    const $token = this.$refs[`token-${this.selectedTokenId}`];

    if ($token) {
      $token.remove();
    }
  },
}));

Alpine.store("mfa", {
  loading: true,
  working: false,
  errors: [],
  enabled: false,
  enrolling: false,
  backupRemaining: 0,
  backupCodes: [],
  secret: "",
  qrDataUrl: "",
});

Alpine.data("MFASettings", () => ({
  async init() {
    await this.loadMFA();
  },

  backupCodesText() {
    return this.$store.mfa.backupCodes.join("\n");
  },

  copyBackupCodes() {
    if (this.$refs.backupCodes) {
      copyToClipboard(this.$refs.backupCodes);
    }
  },

  async loadMFA() {
    this.$store.mfa.loading = true;
    this.$store.mfa.errors = [];

    try {
      const response = await CTFd.fetch("/api/v1/users/me/mfa");
      const result = await response.json();

      if (!response.ok || !result.success) {
        const messages = Object.values(result.errors || {});
        this.$store.mfa.errors = messages.length
          ? messages
          : ["Unable to load multi-factor authentication settings."];

        this.$store.mfa.loading = false;
        return;
      }

      const data = result.data;
      this.$store.mfa.enabled = data.enabled ?? false;
      this.$store.mfa.enrolling = data.enrolling ?? false;
      this.$store.mfa.backupRemaining = data.backup_remaining ?? 0;
      this.$store.mfa.backupCodes = data.backup_codes || [];
      this.$store.mfa.secret = data.secret || "";
      this.$store.mfa.qrDataUrl = data.qrcode
        ? `data:image/png;base64,${data.qrcode}`
        : "";

      this.$store.mfa.loading = false;
    } catch (_error) {
      this.$store.mfa.errors = ["Unable to load multi-factor authentication settings."];
      this.$store.mfa.loading = false;
    }
  },
}));

Alpine.data("MFASetupManager", () => ({
  showSecret: false,
  enableConfirm: "",
  enableCode: "",

  async beginSetup() {
    this.$store.mfa.working = true;
    this.$store.mfa.errors = [];

    try {
      const response = await CTFd.fetch("/api/v1/users/me/mfa/setup", {
        method: "POST",
        body: JSON.stringify({}),
      });

      const result = await response.json();
      if (!response.ok || !result.success) {
        const messages = Object.values(result.errors || {});
        this.$store.mfa.errors = messages.length
          ? messages
          : ["Unable to update multi-factor authentication settings."];

        return;
      }

      const data = result.data;
      this.$store.mfa.enabled = false;
      this.$store.mfa.enrolling = data.enrolling ?? false;
      this.$store.mfa.backupRemaining = 0;
      this.$store.mfa.backupCodes = [];
      this.$store.mfa.secret = data.secret || "";
      this.$store.mfa.qrDataUrl = data.qrcode
        ? `data:image/png;base64,${data.qrcode}`
        : "";
      this.showSecret = false;
    } catch (_error) {
      this.$store.mfa.errors = [
        "Unable to update multi-factor authentication settings.",
      ];
    } finally {
      this.$store.mfa.working = false;
    }
  },

  async cancelSetup() {
    this.$store.mfa.working = true;
    this.$store.mfa.errors = [];

    try {
      const response = await CTFd.fetch("/api/v1/users/me/mfa/setup", {
        method: "DELETE",
        body: JSON.stringify({}),
      });

      const result = await response.json();
      if (!response.ok || !result.success) {
        const messages = Object.values(result.errors || {});
        this.$store.mfa.errors = messages.length
          ? messages
          : ["Unable to update multi-factor authentication settings."];

        return;
      }

      const data = result.data;
      this.$store.mfa.enrolling = data.enrolling ?? false;
      this.$store.mfa.secret = "";
      this.$store.mfa.qrDataUrl = "";
      this.showSecret = false;
      this.enableConfirm = "";
      this.enableCode = "";
    } catch (_error) {
      this.$store.mfa.errors = [
        "Unable to update multi-factor authentication settings.",
      ];
    } finally {
      this.$store.mfa.working = false;
    }
  },

  async enableMFA() {
    this.$store.mfa.working = true;
    this.$store.mfa.errors = [];

    try {
      const response = await CTFd.fetch("/api/v1/users/me/mfa/enable", {
        method: "POST",
        body: JSON.stringify({
          confirm: this.enableConfirm,
          mfa_code: this.enableCode,
        }),
      });

      const result = await response.json();
      if (!response.ok || !result.success) {
        const messages = Object.values(result.errors || {});
        this.$store.mfa.errors = messages.length
          ? messages
          : ["Unable to update multi-factor authentication settings."];

        return;
      }

      const data = result.data;
      this.$store.mfa.enabled = data.enabled ?? false;
      this.$store.mfa.enrolling = data.enrolling ?? false;
      this.$store.mfa.backupRemaining = data.backup_remaining ?? 0;
      this.$store.mfa.backupCodes = data.backup_codes || [];
      this.$store.mfa.secret = "";
      this.$store.mfa.qrDataUrl = "";
      this.showSecret = false;
      this.enableConfirm = "";
      this.enableCode = "";
    } catch (_error) {
      this.$store.mfa.errors = [
        "Unable to update multi-factor authentication settings.",
      ];
    } finally {
      this.$store.mfa.working = false;
    }
  },
}));

Alpine.data("MFABackupManager", () => ({
  regenerateConfirm: "",
  regenerateCode: "",

  async regenerateBackupCodes() {
    this.$store.mfa.working = true;
    this.$store.mfa.errors = [];

    try {
      const response = await CTFd.fetch("/api/v1/users/me/mfa/backup", {
        method: "POST",
        body: JSON.stringify({
          confirm: this.regenerateConfirm,
          mfa_code: this.regenerateCode,
        }),
      });

      const result = await response.json();
      if (!response.ok || !result.success) {
        const messages = Object.values(result.errors || {});
        this.$store.mfa.errors = messages.length
          ? messages
          : ["Unable to update multi-factor authentication settings."];

        return;
      }

      const data = result.data;
      this.$store.mfa.backupRemaining = data.backup_remaining ?? 0;
      this.$store.mfa.backupCodes = data.backup_codes || [];
      this.regenerateConfirm = "";
      this.regenerateCode = "";
    } catch (_error) {
      this.$store.mfa.errors = [
        "Unable to update multi-factor authentication settings.",
      ];
    } finally {
      this.$store.mfa.working = false;
    }
  },
}));

Alpine.data("MFADisableManager", () => ({
  disableUseBackupCode: false,
  disableConfirm: "",
  disableCode: "",
  disableBackupCode: "",

  toggleDisableCodeMode() {
    this.disableUseBackupCode = !this.disableUseBackupCode;
    this.disableCode = "";
    this.disableBackupCode = "";
  },

  async disableMFA() {
    this.$store.mfa.working = true;
    this.$store.mfa.errors = [];

    try {
      const response = await CTFd.fetch("/api/v1/users/me/mfa/disable", {
        method: "POST",
        body: JSON.stringify({
          confirm: this.disableConfirm,
          mfa_code: this.disableUseBackupCode ? "" : this.disableCode,
          mfa_backup_code: this.disableUseBackupCode ? this.disableBackupCode : "",
        }),
      });

      const result = await response.json();
      if (!response.ok || !result.success) {
        const messages = Object.values(result.errors || {});
        this.$store.mfa.errors = messages.length
          ? messages
          : ["Unable to update multi-factor authentication settings."];

        return;
      }

      const data = result.data;
      this.$store.mfa.enabled = data.enabled ?? false;
      this.$store.mfa.enrolling = data.enrolling ?? false;
      this.$store.mfa.backupRemaining = data.backup_remaining ?? 0;
      this.$store.mfa.backupCodes = [];
      this.$store.mfa.secret = "";
      this.$store.mfa.qrDataUrl = "";
      this.disableUseBackupCode = false;
      this.disableConfirm = "";
      this.disableCode = "";
      this.disableBackupCode = "";
    } catch (_error) {
      this.$store.mfa.errors = [
        "Unable to update multi-factor authentication settings.",
      ];
    } finally {
      this.$store.mfa.working = false;
    }
  },
}));

Alpine.start();
