import $ from "jquery";

$(".toggle-button").click(function() {
    this.id = this.value
    function foo (res) {
        $("#"+res.id).html(res.data)
        if(res.data === "enabled"){
            $("#"+res.id).removeClass("bg-danger").addClass("bg-success")
        }else{
            $("#"+res.id).removeClass("bg-success").addClass("bg-danger")
        }}
        $.get(`/admin/emailNotifs/config/${this.value}`,function(res){
            foo(res)
        })
  });