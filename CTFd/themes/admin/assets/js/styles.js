import "bootstrap/dist/js/bootstrap.bundle";
import { makeSortableTables } from "core/utils";
import $ from "jquery";

export default () => {
  // TODO: This is kind of a hack to mimic a React-like state construct.
  // It should be removed once we have a real front-end framework in place.
  $(":input").each(function() {
    $(this).data("initial", $(this).val());
  });

  $(".form-control").bind({
    focus: function() {
      $(this).addClass("input-filled-valid");
    },
    blur: function() {
      if ($(this).val() === "") {
        $(this).removeClass("input-filled-valid");
      }
    }
  });

  $(".modal").on("show.bs.modal", function(e) {
    $(".form-control").each(function() {
      if ($(this).val()) {
        $(this).addClass("input-filled-valid");
      }
    });
  });

  $(function() {
    $(".form-control").each(function() {
      if ($(this).val()) {
        $(this).addClass("input-filled-valid");
      }
    });

    $("tr[data-href], td[data-href]").click(function() {
      var sel = getSelection().toString();
      if (!sel) {
        var href = $(this).attr("data-href");
        if (href) {
          window.location = href;
        }
      }
      return false;
    });

    $("[data-checkbox]").click(function(e) {
      if ($(e.target).is("input[type=checkbox]")) {
        e.stopImmediatePropagation();
        return;
      }
      let checkbox = $(this).find("input[type=checkbox]");
      // Doing it this way with an event allows data-checkbox-all to work
      checkbox.click();
      e.stopImmediatePropagation();
    });

    $("[data-checkbox-all]").on("click change", function(e) {
      const checked = $(this).prop("checked");
      const idx = $(this).index() + 1;
      $(this)
        .closest("table")
        .find(`tr td:nth-child(${idx}) input[type=checkbox]`)
        .prop("checked", checked);
      e.stopImmediatePropagation();
    });

    $("tr[data-href] a, tr[data-href] button").click(function(e) {
      // TODO: This is a hack to allow modal close buttons to work
      if (!$(this).attr("data-dismiss")) {
        e.stopPropagation();
      }
    });

    $(".page-select").change(function() {
      let url = new URL(window.location);
      url.searchParams.set("page", this.value);
      window.location.href = url.toString();
    });

    $('a[data-toggle="tab"]').on("shown.bs.tab", function(e) {
      sessionStorage.setItem("activeTab", $(e.target).attr("href"));
    });

    let activeTab = sessionStorage.getItem("activeTab");
    if (activeTab) {
      let target = $(
        `.nav-tabs a[href="${activeTab}"], .nav-pills a[href="${activeTab}"]`
      );
      if (target.length) {
        target.tab("show");
      } else {
        sessionStorage.removeItem("activeTab");
      }
    }

    makeSortableTables();
    $('[data-toggle="tooltip"]').tooltip();
  });
};
