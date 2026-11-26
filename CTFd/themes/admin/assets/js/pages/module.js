import "./main";
import CTFd from "../compat/CTFd";
import $ from "jquery";
import { ezAlert, ezQuery } from "../compat/ezq";
import { send, setupMembership } from "../membership";

function showErrors(errors) {
  const body = Object.entries(errors || {})
    .map(([key, value]) => {
      const msg = Array.isArray(value) ? value.join(", ") : value;
      return key ? `${key}: ${msg}` : msg;
    })
    .join("<br>");

  ezAlert({
    title: "Error",
    body: body || "Something went wrong.",
    button: "OK",
  });
}

function createModule(event) {
  event.preventDefault();
  const form = event.target;
  const payload = {
    name: form.name.value,
    description: form.description.value || null,
  };

  CTFd.fetch("/api/v1/modules", {
    method: "POST",
    credentials: "same-origin",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((response) => {
      if (response.success) {
        window.location =
          CTFd.config.urlRoot + "/admin/modules/" + response.data.id;
      } else {
        showErrors(response.errors);
      }
    });
}

function updateModule(event) {
  event.preventDefault();
  const form = event.target;
  const payload = {
    name: form.name.value,
    description: form.description.value || null,
  };

  CTFd.fetch("/api/v1/modules/" + window.MODULE_ID, {
    method: "PATCH",
    credentials: "same-origin",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((response) => {
      if (response.success) {
        $("#module-edit-modal").modal("hide");
        window.location.reload();
      } else {
        showErrors(response.errors);
      }
    });
}

function deleteModule(_event) {
  ezQuery({
    title: "Delete Module",
    body: "Are you sure you want to delete this module? Linked challenges will become ungrouped and visible to all.",
    success: function () {
      CTFd.fetch("/api/v1/modules/" + window.MODULE_ID, {
        method: "DELETE",
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      }).then((response) => {
        if (response.ok) {
          window.location = CTFd.config.urlRoot + "/admin/modules";
        }
      });
    },
  });
}

$(() => {
  // New module page
  $("#module-create-form").submit(createModule);

  // Module detail page
  $(".edit-module").click(function () {
    $("#module-edit-modal").modal("toggle");
  });
  $("#module-update-form").submit(updateModule);
  $(".delete-module").click(deleteModule);

  if (window.MODULE_ID === undefined) return;
  const base = "/api/v1/modules/" + window.MODULE_ID;
  setupMembership({
    audiences: {
      label: "Audiences",
      add: (box) =>
        send(base + "/audiences", "POST", { audience_id: +box.dataset.id }),
      remove: (box) => send(base + "/audiences/" + box.dataset.id, "DELETE"),
    },
    challenges: {
      label: "Challenges",
      add: (box) =>
        send(base + "/challenges", "POST", { challenge_id: +box.dataset.id }),
      remove: (box) => send(base + "/challenges/" + box.dataset.id, "DELETE"),
    },
  });
});
