import "bootstrap/dist/js/bootstrap.bundle";
import $ from "jquery";

export default () => {
  // TODO: This is kind of a hack to mimic a React-like state construct.
  // It should be removed once we have a real front-end framework in place.
  $(":input").each(function() {
    $(this).data("initial", $(this).val());
  });

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

  $(".page-select").change(function() {
    let url = new URL(window.location);
    url.searchParams.set("page", this.value);
    window.location.href = url.toString();
  });

  $('[data-toggle="tooltip"]').tooltip();
};
