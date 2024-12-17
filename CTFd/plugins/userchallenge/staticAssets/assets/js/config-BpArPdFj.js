import{$ as e}from"../jquery-BT3bhPE2.js";e("#toggle-button").click(()=>{e.get("/userchallenge/api/config",function(l){e("#label-enable").html("challenge creation is "+l.data)})});
