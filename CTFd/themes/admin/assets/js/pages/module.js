import "./main";
import CTFd from "../compat/CTFd";
import $ from "jquery";
import { ezAlert, ezQuery } from "../compat/ezq";

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

function linkAudience(event) {
  event.preventDefault();
  const audienceId = parseInt(
    $(event.target).find("[name=audience_id]").val(),
    10,
  );
  if (!audienceId) return;

  CTFd.fetch("/api/v1/modules/" + window.MODULE_ID + "/audiences", {
    method: "POST",
    credentials: "same-origin",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ audience_id: audienceId }),
  })
    .then((response) => response.json())
    .then((response) => {
      if (response.success) {
        window.location.reload();
      } else {
        showErrors(response.errors);
      }
    });
}

function unlinkAudience(event) {
  const audienceId = $(event.currentTarget).data("unlink-audience");
  ezQuery({
    title: "Unlink Audience",
    body: "Are you sure you want to unlink this audience?",
    success: function () {
      CTFd.fetch(
        "/api/v1/modules/" + window.MODULE_ID + "/audiences/" + audienceId,
        {
          method: "DELETE",
          credentials: "same-origin",
          headers: { Accept: "application/json" },
        },
      ).then((response) => {
        if (response.ok) window.location.reload();
      });
    },
  });
}

function addChallenges(event) {
  event.preventDefault();
  const select = $("#add-challenges-select");
  const ids = select
    .find("option:selected")
    .map(function () {
      return parseInt($(this).val(), 10);
    })
    .get();
  if (!ids.length) return;

  $("#add-challenges-submit").prop("disabled", true);
  const reqs = ids.map((id) =>
    CTFd.fetch("/api/v1/modules/" + window.MODULE_ID + "/challenges", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ challenge_id: id }),
    })
      .then((response) => response.json())
      .catch(() => ({ success: false })),
  );

  Promise.all(reqs).then((responses) => {
    const failed = responses.filter((r) => !r.success);
    if (failed.length) {
      ezAlert({
        title: "Error",
        body: `${failed.length} of ${ids.length} could not be added.`,
        button: "OK",
        success: function () {
          window.location.reload();
        },
      });
    } else {
      window.location.reload();
    }
  });
}

function removeChallenge(event) {
  const challengeId = $(event.currentTarget).data("remove-challenge");
  ezQuery({
    title: "Remove Challenge",
    body: "Remove this challenge from this module? It stays in any other modules it belongs to.",
    success: function () {
      CTFd.fetch(
        "/api/v1/modules/" + window.MODULE_ID + "/challenges/" + challengeId,
        {
          method: "DELETE",
          credentials: "same-origin",
          headers: { Accept: "application/json" },
        },
      ).then((response) => {
        if (response.ok) window.location.reload();
      });
    },
  });
}

function selectedChallengeIds() {
  return $("input[data-module-challenge-id]:checked")
    .map(function () {
      return $(this).data("module-challenge-id");
    })
    .get();
}

function removeSelectedChallenges(_event) {
  const ids = selectedChallengeIds();
  if (!ids.length) return;
  const target = ids.length === 1 ? "challenge" : "challenges";

  ezQuery({
    title: "Remove Challenges",
    body: `Remove ${ids.length} ${target} from this module? They stay in any other modules they belong to.`,
    success: function () {
      const reqs = ids.map((id) =>
        CTFd.fetch(
          "/api/v1/modules/" + window.MODULE_ID + "/challenges/" + id,
          {
            method: "DELETE",
            credentials: "same-origin",
            headers: { Accept: "application/json" },
          },
        ).catch(() => ({ ok: false })),
      );
      Promise.all(reqs).then((responses) => {
        const failed = responses.filter((r) => !r.ok).length;
        if (failed) {
          ezAlert({
            title: "Error",
            body: `${failed} of ${ids.length} could not be removed.`,
            button: "OK",
            success: function () {
              window.location.reload();
            },
          });
        } else {
          window.location.reload();
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
  $("#link-audience-form").submit(linkAudience);
  $("[data-unlink-audience]").click(unlinkAudience);
  $("#add-challenges-form").submit(addChallenges);
  $("[data-remove-challenge]").click(removeChallenge);
  $("#remove-challenges-button").click(removeSelectedChallenges);
  $("input[data-module-challenge-id], input[data-checkbox-all]").on(
    "change",
    function () {
      $("#remove-challenges-button").prop(
        "disabled",
        selectedChallengeIds().length === 0,
      );
    },
  );

  const addSelect = $("#add-challenges-select");
  if (addSelect.length) {
    addSelect.on("change", function () {
      $("#add-challenges-submit").prop(
        "disabled",
        addSelect.find("option:selected").length === 0,
      );
    });
  }
});
