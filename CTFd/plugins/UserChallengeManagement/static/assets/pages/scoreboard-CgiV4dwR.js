import{$ as i,C as n,A as l}from"./main-D_lcMXdT.js";const d={users:(e,s)=>n.api.patch_user_public({userId:e},s),teams:(e,s)=>n.api.patch_team_public({teamId:e},s)};function u(){const e=i(this),s=e.data("account-id"),a=e.data("state");let t;a==="visible"?t=!0:a==="hidden"&&(t=!1);const o={hidden:t};d[n.config.userMode](s,o).then(c=>{c.success&&(t?(e.data("state","hidden"),e.addClass("btn-danger").removeClass("btn-success"),e.text("Hidden")):(e.data("state","visible"),e.addClass("btn-success").removeClass("btn-danger"),e.text("Visible")))})}function r(e,s){const a={hidden:s==="hidden"},t=[];for(let o of e.accounts)t.push(d[n.config.userMode](o,a));for(let o of e.users)t.push(d.users(o,a));Promise.all(t).then(o=>{window.location.reload()})}function b(e){let s=i(".tab-pane.active input[data-account-id]:checked").map(function(){return i(this).data("account-id")}),a=i(".tab-pane.active input[data-user-id]:checked").map(function(){return i(this).data("user-id")}),t={accounts:s,users:a};l({title:"Toggle Visibility",body:i(`
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
    `),button:"Submit",success:function(){let c=i("#scoreboard-bulk-edit").serializeJSON(!0).visibility;r(t,c)}})}i(()=>{i(".scoreboard-toggle").click(u),i("#scoreboard-edit-button").click(b)});
