import{$ as e,u as d,C as n,A as u}from"./main-D_lcMXdT.js";function r(l){let t=e("input[data-team-id]:checked").map(function(){return e(this).data("team-id")}),o=t.length===1?"team":"teams";d({title:"Delete Teams",body:`Are you sure you want to delete ${t.length} ${o}?`,success:function(){const a=[];for(var i of t)a.push(n.fetch(`/api/v1/teams/${i}`,{method:"DELETE"}));Promise.all(a).then(s=>{window.location.reload()})}})}function m(l){let t=e("input[data-team-id]:checked").map(function(){return e(this).data("team-id")});u({title:"Edit Teams",body:e(`
    <form id="teams-bulk-edit">
      <div class="form-group">
        <label>Banned</label>
        <select name="banned" data-initial="">
          <option value="">--</option>
          <option value="true">True</option>
          <option value="false">False</option>
        </select>
      </div>
      <div class="form-group">
        <label>Hidden</label>
        <select name="hidden" data-initial="">
          <option value="">--</option>
          <option value="true">True</option>
          <option value="false">False</option>
        </select>
      </div>
    </form>
    `),button:"Submit",success:function(){let o=e("#teams-bulk-edit").serializeJSON(!0);const a=[];for(var i of t)a.push(n.fetch(`/api/v1/teams/${i}`,{method:"PATCH",body:JSON.stringify(o)}));Promise.all(a).then(s=>{window.location.reload()})}})}e(()=>{e("#teams-delete-button").click(r),e("#teams-edit-button").click(m)});
