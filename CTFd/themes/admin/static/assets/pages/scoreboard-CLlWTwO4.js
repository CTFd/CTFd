import{$ as d,C as l,A as f}from"./main-sbGV3kXM.js";import{l as p}from"../index-TjCxX7sJ.js";const u={users:(e,a)=>l.api.patch_user_public({userId:e},a),teams:(e,a)=>l.api.patch_team_public({teamId:e},a)},b=p("http://127.0.0.1:4000");b.on("connect",function(){console.log("Conectado al servidor")});function h(){const e=d(this),a=e.data("account-id"),i=e.data("state");let t;i==="visible"?t=!0:i==="hidden"&&(t=!1);const n={hidden:t};u[l.config.userMode](a,n).then(s=>{s.success&&(t?(e.data("state","hidden"),e.addClass("btn-danger").removeClass("btn-success"),e.text("Hidden")):(e.data("state","visible"),e.addClass("btn-success").removeClass("btn-danger"),e.text("Visible")))})}function m(e,a){const i={hidden:a==="hidden"},t=[];for(let n of e.accounts)t.push(u[l.config.userMode](n,i));for(let n of e.users)t.push(u.users(n,i));Promise.all(t).then(n=>{window.location.reload()})}function g(e){let a=d(".tab-pane.active input[data-account-id]:checked").map(function(){return d(this).data("account-id")}),i=d(".tab-pane.active input[data-user-id]:checked").map(function(){return d(this).data("user-id")}),t={accounts:a,users:i};f({title:"Toggle Visibility",body:d(`
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
    `),button:"Submit",success:function(){let s=d("#scoreboard-bulk-edit").serializeJSON(!0).visibility;m(t,s)}})}d(()=>{d(".scoreboard-toggle").click(h),d("#scoreboard-edit-button").click(g)});function $(e,a){const i=l.config.userMode;let t;return a?i==="teams"?t=`/admin/teams/${e}`:t=`/admin/users/${e}`:i==="teams"?t=`/teams/${e}`:t=`/users/${e}`,t}function v(e,a={}){const i=window.location.origin,n={"admin.users_detail":"/admin/users/<user_id>","admin.teams_detail":"/admin/teams/<team_id>"}[e];if(!n)return console.error(`Route not found: ${e}`),"";let s=n;for(const[o,c]of Object.entries(a)){const r=`<${o}>`;s.includes(r)&&(s=s.replace(r,c))}return i+s}function _(e){const a=e.standings,i=e.user_standings,t=e.mode;let n="";if(a.forEach((s,o)=>{const c=$(s.id,!0);n+=`
      <tr data-href="${c}">
        <td class="border-right text-center" data-checkbox>
          <div class="form-check">
            <input type="checkbox" class="form-check-input" value="${s.id}" data-account-id="${s.id}" autocomplete="off">&nbsp;
          </div>
        </td>
        <td class="text-center" width="10%">${o+1}</td>
        <td>
          <a href="${c}">
            ${s.name}
            ${s.oauth_id?'<span class="badge badge-primary">Official</span>':""}
          </a>
        </td>
        <td>${s.score}</td>
        <td>
          ${s.hidden?'<span class="badge badge-danger">hidden</span>':'<span class="badge badge-success">visible</span>'}
        </td>
      </tr>
    `}),d("#standings-table-body").html(n),t==="teams"&&i){let s="";i.forEach((o,c)=>{const r=v("admin.users_detail",{user_id:o.user_id});s+=`
        <tr data-href="${r}">
          <td class="border-right text-center" data-checkbox>
            <div class="form-check">
              <input type="checkbox" class="form-check-input" value="${o.user_id}" autocomplete="off" data-user-id="${o.user_id}">&nbsp;
            </div>
          </td>
          <td class="text-center" width="10%">${c+1}</td>
          <td>
            <a href="${r}">
              ${o.name}
              ${o.oauth_id?'<span class="badge badge-primary">Official</span>':""}
            </a>
          </td>
          <td>${o.score}</td>
          <td>
            ${o.hidden?'<span class="badge badge-danger">hidden</span>':'<span class="badge badge-success">visible</span>'}
          </td>
        </tr>
      `}),d("#user-standings-table-body").html(s)}}b.on("scoreboard_update",function(e){console.log(e),_(e.data)});d(document).ready(function(){b.emit("request_initial_data")});
