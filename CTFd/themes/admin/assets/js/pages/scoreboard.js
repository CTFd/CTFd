import "./main";
import CTFd from "../compat/CTFd";
import $ from "jquery";
import "../compat/json";
import { ezAlert } from "../compat/ezq";
import { io } from "socket.io-client";

const api_func = {
  users: (x, y) => CTFd.api.patch_user_public({ userId: x }, y),
  teams: (x, y) => CTFd.api.patch_team_public({ teamId: x }, y),
};

const socket = io('http://127.0.0.1:4000');

socket.on('connect', function () {
  console.log('Conectado al servidor');
});

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
    hidden: hidden,
  };

  api_func[CTFd.config.userMode](id, params).then((response) => {
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

function toggleSelectedAccounts(selectedAccounts, action) {
  const params = {
    hidden: action === "hidden" ? true : false,
  };
  const reqs = [];
  for (let accId of selectedAccounts.accounts) {
    reqs.push(api_func[CTFd.config.userMode](accId, params));
  }
  for (let accId of selectedAccounts.users) {
    reqs.push(api_func["users"](accId, params));
  }
  Promise.all(reqs).then((_responses) => {
    window.location.reload();
  });
}

function bulkToggleAccounts(_event) {
  // Get selected account and user IDs but only on the active tab.
  // Technically this could work for both tabs at the same time but that seems like
  // bad behavior. We don't want to accidentally unhide a user/team accidentally
  let accountIDs = $(".tab-pane.active input[data-account-id]:checked").map(
    function () {
      return $(this).data("account-id");
    },
  );

  let userIDs = $(".tab-pane.active input[data-user-id]:checked").map(
    function () {
      return $(this).data("user-id");
    },
  );

  let selectedUsers = {
    accounts: accountIDs,
    users: userIDs,
  };

  ezAlert({
    title: "Toggle Visibility",
    body: $(`
    <form id="scoreboard-bulk-edit">
      <div class="form-group">
        <label>Visibility</label>
        <select name="visibility" data-initial="">
          <option value="">--</option>
          <option value="visible">Visible</option>
          <option value="hidden">Hidden</option>
        </select>
      </div>
    </form>
    `),
    button: "Submit",
    success: function () {
      let data = $("#scoreboard-bulk-edit").serializeJSON(true);
      let state = data.visibility;
      toggleSelectedAccounts(selectedUsers, state);
    },
  });
}

$(() => {
  $(".scoreboard-toggle").click(toggleAccount);
  $("#scoreboard-edit-button").click(bulkToggleAccounts);
});


function generateAccountUrl(accountId, admin) {
  const mode = CTFd.config.userMode;
  let url;

  if (admin) {
    if (mode === 'teams') {
      url = `/admin/teams/${accountId}`;
    } else {
      url = `/admin/users/${accountId}`;
    }
  } else {
    if (mode === 'teams') {
      url = `/teams/${accountId}`;
    } else {
      url = `/users/${accountId}`;
    }
  }

  return url;
}

function generateUrl(routeName, params = {}) {
  const baseUrl = window.location.origin;
  const routes = {
    'admin.users_detail': '/admin/users/<user_id>',
    'admin.teams_detail': '/admin/teams/<team_id>',
  };

  const pattern = routes[routeName];
  if (!pattern) {
    console.error(`Route not found: ${routeName}`);
    return '';
  }

  let url = pattern;
  for (const [key, value] of Object.entries(params)) {
    const placeholder = `<${key}>`;
    if (url.includes(placeholder)) {
      url = url.replace(placeholder, value);
    }
  }

  return baseUrl + url;
}

function renderScoreboard(data) {
  const standings = data.standings;
  const userStandings = data.user_standings;
  const mode = data.mode;

  let html = '';
  standings.forEach((team, index) => {
    const teamUrl = generateAccountUrl(team.id, true);
    html += `
      <tr data-href="${teamUrl}">
        <td class="border-right text-center" data-checkbox>
          <div class="form-check">
            <input type="checkbox" class="form-check-input" value="${team.id}" data-account-id="${team.id}" autocomplete="off">&nbsp;
          </div>
        </td>
        <td class="text-center" width="10%">${index + 1}</td>
        <td>
          <a href="${teamUrl}">
            ${team.name}
            ${team.oauth_id ? '<span class="badge badge-primary">Official</span>' : ''}
          </a>
        </td>
        <td>${team.score}</td>
        <td>
          ${team.hidden ? '<span class="badge badge-danger">hidden</span>' : '<span class="badge badge-success">visible</span>'}
        </td>
      </tr>
    `;
  });
  $('#standings-table-body').html(html);

  if (mode === 'teams' && userStandings) {
    let userHtml = '';
    userStandings.forEach((user, index) => {
      const userUrl = generateUrl('admin.users_detail', { user_id: user.user_id });
      userHtml += `
        <tr data-href="${userUrl}">
          <td class="border-right text-center" data-checkbox>
            <div class="form-check">
              <input type="checkbox" class="form-check-input" value="${user.user_id}" autocomplete="off" data-user-id="${user.user_id}">&nbsp;
            </div>
          </td>
          <td class="text-center" width="10%">${index + 1}</td>
          <td>
            <a href="${userUrl}">
              ${user.name}
              ${user.oauth_id ? '<span class="badge badge-primary">Official</span>' : ''}
            </a>
          </td>
          <td>${user.score}</td>
          <td>
            ${user.hidden ? '<span class="badge badge-danger">hidden</span>' : '<span class="badge badge-success">visible</span>'}
          </td>
        </tr>
      `;
    });
    $('#user-standings-table-body').html(userHtml);
  }
}

socket.on('scoreboard_update', function (data) {
  renderScoreboard(data.data);
});

$(document).ready(function () {
  socket.emit('request_initial_data');
});