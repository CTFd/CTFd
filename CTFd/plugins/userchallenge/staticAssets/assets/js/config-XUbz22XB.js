import{$ as e}from"../jquery-CHTzeeNo.js";e("#toggle-button").click(()=>{e.get("/userchallenge/api/config",function(l){e("#label-enable").html("challenge creation is "+l.data)})});
