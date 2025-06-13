import $ from "jquery";
$("#toggle-button").click(()=>{
    $.get("/userchallenge/api/config",function (res){
        $("#label-enable").html(res.data)
        if(res.data === "enabled"){
            $("#toggle-button").removeClass("bg-danger").addClass("bg-success")
        }else{
            $("#toggle-button").removeClass("bg-success").addClass("bg-danger")
        }
    })
})