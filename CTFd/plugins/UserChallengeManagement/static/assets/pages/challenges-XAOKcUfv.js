import{$ as e,u as c,C as i,A as d}from"./main-D_lcMXdT.js";function u(o){let l=e("input[data-challenge-id]:checked").map(function(){return e(this).data("challenge-id")}),a=l.length===1?"challenge":"challenges";c({title:"Delete Challenges",body:`Are you sure you want to delete ${l.length} ${a}?`,success:function(){const t=[];for(var n of l)t.push(i.fetch(`/api/v1/challenges/${n}`,{method:"DELETE"}));Promise.all(t).then(s=>{window.location.reload()})}})}function r(o){let l=e("input[data-challenge-id]:checked").map(function(){return e(this).data("challenge-id")});d({title:"Edit Challenges",body:e(`
    <form id="challenges-bulk-edit">
      <div class="form-group">
        <label>Category</label>
        <input type="text" name="category" data-initial="" value="">
      </div>
      <div class="form-group">
        <label>Value</label>
        <input type="number" name="value" data-initial="" value="">
      </div>
      <div class="form-group">
        <label>State</label>
        <select name="state" data-initial="">
          <option value="">--</option>
          <option value="visible">Visible</option>
          <option value="hidden">Hidden</option>
        </select>
      </div>
    </form>
    `),button:"Submit",success:function(){let a=e("#challenges-bulk-edit").serializeJSON(!0);const t=[];for(var n of l)t.push(i.fetch(`/api/v1/challenges/${n}`,{method:"PATCH",body:JSON.stringify(a)}));Promise.all(t).then(s=>{window.location.reload()})}})}e(()=>{e("#challenges-delete-button").click(u),e("#challenges-edit-button").click(r)});
