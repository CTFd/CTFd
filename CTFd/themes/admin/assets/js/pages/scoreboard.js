import "./main";
import CTFd from "core/CTFd";
import $ from "jquery";
import { ezQuery } from "core/ezq";

const api_func = {
  users: (x, y) => CTFd.api.patch_user_public({ userId: x }, y),
  teams: (x, y) => CTFd.api.patch_team_public({ teamId: x }, y)
};

function toggleAccount() {
  const $btn = $(this);
  const id = $btn.data("account-id");
  const state = $btn.data("state");
  let hidden = undefined;
  if (state === "visible") {
    hidden = true;
  } else if (state === "hidden") {
    hidden = false;
  }

  const params = {
    hidden: hidden
  };

  api_func[CTFd.config.userMode](id, params).then(response => {
    if (response.success) {
      if (hidden) {
        $btn.data("state", "hidden");
        $btn.addClass("btn-danger").removeClass("btn-success");
        $btn.text("Hidden");
      } else {
        $btn.data("state", "visible");
        $btn.addClass("btn-success").removeClass("btn-danger");
        $btn.text("Visible");
      }
    }
  });
}

function toggleSelectedAccounts(accountIDs, action) {
  const params = {
    hidden: action === "hide" ? true : false
  };
  const reqs = [];
  for (var accId of accountIDs) {
    reqs.push(api_func[CTFd.config.userMode](accId, params));
  }
  Promise.all(reqs).then(responses => {
    window.location.reload();
  });
}

function hideSelectedAccounts(event) {
  let accountIDs = $("input[data-account-id]:checked").map(function() {
    return $(this).data("account-id");
  });
  let target = accountIDs.length === 1 ? "account" : "accounts";
  ezQuery({
    title: "Hide Accounts",
    body: `Are you sure you want to hide ${accountIDs.length} ${target}?`,
    success: function() {
      toggleSelectedAccounts(accountIDs, "hide");
    }
  });
}

function showSelectedAccounts(event) {
  let accountIDs = $("input[data-account-id]:checked").map(function() {
    return $(this).data("account-id");
  });
  let target = accountIDs.length === 1 ? "account" : "accounts";
  ezQuery({
    title: "Unhide Accounts",
    body: `Are you sure you want to unhide ${accountIDs.length} ${target}?`,
    success: function() {
      toggleSelectedAccounts(accountIDs, "show");
    }
  });
}

function toggleScoreboardSelect(event) {
  const checked = $(this).prop("checked");
  $(this)
    .closest("table")
    .find("input[data-account-id]")
    .prop("checked", checked);
}

$(() => {
  $(".scoreboard-toggle").click(toggleAccount);
  $("#scoreboard-bulk-select").click(toggleScoreboardSelect);
  $("#scoreboard-hide-button").click(hideSelectedAccounts);
  $("#scoreboard-show-button").click(showSelectedAccounts);
});
