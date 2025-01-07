import Alpine from "alpinejs";
import CTFd from "./base";
import { initModal, generateModal } from "./modal";
import { serializeJSON } from "@ctfdio/ctfd-js/forms";
import { copyToClipboard } from "./utils/clipboard";
import { _ } from './utils/i18n.js';

Alpine.data("TeamEditModal", () => ({
    success: null,
    error: null,
    initial: null,
    submitting: false,
    errors: [],

    init() {
        this.initial = serializeJSON(this.$el.querySelector("form"));
    },

    async updateProfile() {
        let data = serializeJSON(this.$el, this.initial, true);

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

        this.errors = [];
        this.submitting = true;
        let response = await CTFd.pages.teams.updateTeamSettings(data);
        this.submitting = false;
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
    }
}));

Alpine.data("TeamCaptainModal", () => ({
    success: null,
    error: null,
    errors: [],

    async updateCaptain() {
        let data = serializeJSON(this.$el, null, true);
        let response = await CTFd.pages.teams.updateTeamSettings(data);

        if (response.success) {
            window.location.reload();
        } else {
            this.success = false;
            this.error = true;
            Object.keys(response.errors).map(error => {
                const error_msg = response.errors[error];
                this.errors.push(error_msg);
            });
        }
    }
}));

Alpine.data("TeamInviteModal", () => ({
    copy() {
        copyToClipboard(this.$refs.link);
    }
}));

Alpine.data("TeamDisbandModal", () => ({
    errors: [],

    async disbandTeam() {
        let response = await CTFd.pages.teams.disbandTeam();

        if (response.success) {
            window.location.reload();
        } else {
            this.errors = response.errors[""];
        }
    }
}));

Alpine.data("CaptainMenu", () => ({
    captain: false,
    teamEditModal: null,
    teamCaptainModal: null,
    teamInviteModal: null,
    teamDisbandModal: null,

    init() {
        this.teamEditModal = document.getElementById("teamEditModal");
        const teamEditModalClose = document.getElementById("teamEditModalClose");
        initModal(teamEditModal, [], [teamEditModalClose]);
        this.teamCaptainModal = document.getElementById("teamCaptainModal");
        const teamCaptainModalClose = document.getElementById("teamCaptainModalClose");
        initModal(teamCaptainModal, [], [teamCaptainModalClose]);
        this.teamInviteModal = document.getElementById("teamInviteModal");
        const teamInviteModalClose = document.getElementById("teamInviteModalClose");
        initModal(teamInviteModal, [], [teamInviteModalClose]);
        this.teamDisbandModal = document.getElementById("teamDisbandModal");
        const teamDisbandModalClose = document.getElementById("teamDisbandModalClose");
        initModal(teamDisbandModal, [], [teamDisbandModalClose]);
    },

    editTeam() {
        this.teamEditModal.showModal();
    },

    chooseCaptain() {
        this.teamCaptainModal.showModal();
    },

    async inviteMembers() {
        const response = await CTFd.pages.teams.getInviteToken();

        if (response.success) {
            const code = response.data.code;
            const url = `${window.location.origin}${CTFd.config.urlRoot}/teams/invite?code=${code}`;

            document.querySelector("#teamInviteModal input[name=link]").value = url;
            this.$store.inviteToken = url;
            this.teamInviteModal.showModal();
        } else {
            console.log(response);
            generateModal(_("Invite users"), response.errors[""].join("<br>"));
        }
    },

    disbandTeam() {
        this.teamDisbandModal.showModal();
    }
}));

// Alpine.start();
