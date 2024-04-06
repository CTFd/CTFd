import{$ as e,u as r,C as l,A as u}from"./main-D_lcMXdT.js";function d(a){let t=e("input[data-user-id]:checked").map(function(){return e(this).data("user-id")}),i=t.length===1?"user":"users";r({title:"Delete Users",body:`Are you sure you want to delete ${t.length} ${i}?`,success:function(){const o=[];for(var s of t)o.push(l.fetch(`/api/v1/users/${s}`,{method:"DELETE"}));Promise.all(o).then(n=>{window.location.reload()})}})}function c(a){let t=e("input[data-user-id]:checked").map(function(){return e(this).data("user-id")});u({title:"Edit Users",body:e(`
    <form id="users-bulk-edit">
      <div class="form-group">
        <label>Verified</label>
        <select name="verified" data-initial="">
          <option value="">--</option>
          <option value="true">True</option>
          <option value="false">False</option>
        </select>
      </div>
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
    `),button:"Submit",success:function(){let i=e("#users-bulk-edit").serializeJSON(!0);const o=[];for(var s of t)o.push(l.fetch(`/api/v1/users/${s}`,{method:"PATCH",body:JSON.stringify(i)}));Promise.all(o).then(n=>{window.location.reload()})}})}e(()=>{e("#users-delete-button").click(d),e("#users-edit-button").click(c)});
