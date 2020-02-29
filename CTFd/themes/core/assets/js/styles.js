import "bootstrap/dist/js/bootstrap.bundle";
import $ from "jquery";

export default () => {
  $(".form-control").bind({
    focus: function() {
      $(this).removeClass("input-filled-invalid");
      $(this).addClass("input-filled-valid");
    },
    blur: function() {
      if ($(this).val() === "") {
        $(this).removeClass("input-filled-invalid");
        $(this).removeClass("input-filled-valid");
      }
    }
  });

  $(".form-control").each(function() {
    if ($(this).val()) {
      $(this).addClass("input-filled-valid");
    }
  });

  $('[data-toggle="tooltip"]').tooltip();
};
