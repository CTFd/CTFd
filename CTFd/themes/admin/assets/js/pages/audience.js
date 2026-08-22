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

function createAudience(event) {
  event.preventDefault();
  const form = event.target;
  const payload = {
    name: form.name.value,
    description: form.description.value || null,
  };

  CTFd.fetch("/api/v1/audiences", {
    method: "POST",
    credentials: "same-origin",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((response) => {
      if (response.success) {
        window.location =
          CTFd.config.urlRoot + "/admin/audiences/" + response.data.id;
      } else {
        showErrors(response.errors);
      }
    });
}

function updateAudience(event) {
  event.preventDefault();
  const form = event.target;
  const payload = {
    name: form.name.value,
    description: form.description.value || null,
  };

  CTFd.fetch("/api/v1/audiences/" + window.AUDIENCE_ID, {
    method: "PATCH",
    credentials: "same-origin",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((response) => {
      if (response.success) {
        $("#audience-edit-modal").modal("hide");
        window.location.reload();
      } else {
        showErrors(response.errors);
      }
    });
}

function deleteAudience(_event) {
  ezQuery({
    title: "Delete Audience",
    body: "Are you sure you want to delete this audience?",
    success: function () {
      CTFd.fetch("/api/v1/audiences/" + window.AUDIENCE_ID, {
        method: "DELETE",
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      }).then((response) => {
        if (response.ok) {
          window.location = CTFd.config.urlRoot + "/admin/audiences";
        }
      });
    },
  });
}

function addMember(event) {
  event.preventDefault();
  const accountId = $("#add-member-account-id").val();
  if (!accountId) return;
  const payload =
    window.USER_MODE === "teams"
      ? { team_id: parseInt(accountId, 10) }
      : { user_id: parseInt(accountId, 10) };

  CTFd.fetch("/api/v1/audiences/" + window.AUDIENCE_ID + "/members", {
    method: "POST",
    credentials: "same-origin",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(payload),
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

function removeMember(event) {
  const memberId = $(event.currentTarget).data("remove-member");
  ezQuery({
    title: "Remove Member",
    body: "Are you sure you want to remove this member?",
    success: function () {
      CTFd.fetch(
        "/api/v1/audiences/" + window.AUDIENCE_ID + "/members/" + memberId,
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

function linkModule(event) {
  event.preventDefault();
  const moduleId = parseInt($(event.target).find("[name=module_id]").val(), 10);
  if (!moduleId) return;

  CTFd.fetch("/api/v1/modules/" + moduleId + "/audiences", {
    method: "POST",
    credentials: "same-origin",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ audience_id: window.AUDIENCE_ID }),
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

function unlinkModule(event) {
  const moduleId = $(event.currentTarget).data("unlink-module");
  ezQuery({
    title: "Unlink Module",
    body: "Are you sure you want to unlink this module from the audience?",
    success: function () {
      CTFd.fetch(
        "/api/v1/modules/" + moduleId + "/audiences/" + window.AUDIENCE_ID,
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

// Debounced account search that fills the hidden account_id field on selection.
function setupMemberSearch() {
  const searchInput = $("#add-member-search");
  if (!searchInput.length) return;

  const suggestions = $("#add-member-suggestions");
  const accountField = $("#add-member-account-id");
  const submitBtn = $("#add-member-submit");
  const hint = $("#add-member-hint");
  const endpoint =
    window.USER_MODE === "teams" ? "/api/v1/teams" : "/api/v1/users";
  let searchTimer = null;

  function renderSuggestions(items) {
    suggestions.empty();
    if (!items.length) {
      suggestions.hide();
      hint.text("No matches.");
      return;
    }
    items.forEach((it) => {
      const li = $("<li>")
        .addClass("list-group-item list-group-item-action")
        .css("cursor", "pointer")
        .text(it.name + " (#" + it.id + ")")
        .on("click", function () {
          searchInput.val(it.name);
          accountField.val(it.id);
          submitBtn.prop("disabled", false);
          suggestions.hide();
          hint.text("Will add: " + it.name + " (#" + it.id + ")");
        });
      suggestions.append(li);
    });
    suggestions.show();
  }

  searchInput.on("input", function () {
    accountField.val("");
    submitBtn.prop("disabled", true);
    const q = $(this).val().trim();
    if (searchTimer) clearTimeout(searchTimer);
    if (!q) {
      suggestions.hide();
      hint.text("Start typing to search.");
      return;
    }
    hint.text("Searching…");
    searchTimer = setTimeout(function () {
      CTFd.fetch(endpoint + "?field=name&q=" + encodeURIComponent(q), {
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      })
        .then((response) => response.json())
        .then((response) => {
          if (response.success) {
            renderSuggestions((response.data || []).slice(0, 20));
          } else {
            hint.text("Search failed.");
          }
        })
        .catch(() => hint.text("Search failed."));
    }, 200);
  });
}

$(() => {
  // New audience page
  $("#audience-create-form").submit(createAudience);

  // Audience detail page
  $(".edit-audience").click(function () {
    $("#audience-edit-modal").modal("toggle");
  });
  $("#audience-update-form").submit(updateAudience);
  $(".delete-audience").click(deleteAudience);
  $("#add-member-form").submit(addMember);
  $("[data-remove-member]").click(removeMember);
  $("#link-module-form").submit(linkModule);
  $("[data-unlink-module]").click(unlinkModule);
  setupMemberSearch();
});
