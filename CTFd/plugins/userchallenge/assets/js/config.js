import $ from "jquery";
$("#toggle-button").click(()=>{
    $.get("/userchallenge/api/config",function (res){
        $("#label-enable").html("challenge creation is " + res.data)
    })
})