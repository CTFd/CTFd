import $ from "jquery";
$("#toggle-button").click(()=>{
    $.get("/userchallenge/api/config",function (res){
        console.log(res.data)
        $("#label-enable").html("challenge creation is " + res.data)
    })
})