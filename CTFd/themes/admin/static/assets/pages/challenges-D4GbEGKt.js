import{$ as e,u as c,C as n,B as r}from"./main-CcyKUC_q.js";function h(d){let i=e("input[data-challenge-id]:checked").map(function(){return e(this).data("challenge-id")}),a=i.length===1?"challenge":"challenges";c({title:"Delete Challenges",body:`Are you sure you want to delete ${i.length} ${a}?`,success:function(){const t=[];for(var l of i)t.push(n.fetch(`/api/v1/challenges/${l}`,{method:"DELETE"}));Promise.all(t).then(o=>{window.location.reload()})}})}function p(d){let i=e("input[data-challenge-id]:checked").map(function(){return e(this).data("challenge-id")}),a=e("input[data-challenge-id]:checked").map(function(){return e(this).data("solution-id")});r({title:"Edit Challenges",body:e(`
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
      <div class="form-group">
        <label>Solution</label>
        <select name="solution" data-initial="">
          <option value="">--</option>
          <option value="visible">Visible</option>
          <option value="hidden">Hidden</option>
          <option value="solved">Solved</option>
        </select>
      </div>
    </form>
    `),button:"Submit",success:function(){const t=[];let l=e("#challenges-bulk-edit").serializeJSON(!0),o={state:l.solution};if(delete l.solution,Object.keys(l).length!==0)for(var u of i)t.push(n.fetch(`/api/v1/challenges/${u}`,{method:"PATCH",body:JSON.stringify(l)}));if(o.state)for(var s of a)s&&t.push(n.fetch(`/api/v1/solutions/${s}`,{method:"PATCH",body:JSON.stringify(o)}));Promise.all(t).then(g=>{window.location.reload()})}})}e(()=>{e("#challenges-delete-button").click(h),e("#challenges-edit-button").click(p)});
