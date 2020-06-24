import "bootstrap/dist/js/bootstrap.bundle";
import { makeSortableTables } from "core/utils";
import $ from "jquery";
import EasyMDE from "easymde";

export function bindMarkdownEditors() {
  $("textarea.markdown").each(function(_i, e) {
    if (e.hasOwnProperty("mde") === false) {
      let mde = new EasyMDE({
        autoDownloadFontAwesome: false,
        toolbar: [
          "bold",
          "italic",
          "heading",
          "|",
          "quote",
          "unordered-list",
          "ordered-list",
          "|",
          "link",
          "image",
          {
            name: "media",
            action: function (editor){
              alert();
            },
            className: "fas fa-file-upload",
            title: "Media Library",
          },
          "|",
          "preview",
          "guide"
        ],
        element: this,
        initialValue: $(this).val(),
        forceSync: true,
        minHeight: "200px"
      });
      this.mde = mde;
      this.codemirror = mde.codemirror;
      $(this).on("change keyup paste", function() {
        mde.codemirror.getDoc().setValue($(this).val());
        mde.codemirror.refresh();
      });
    }
  });
}

export default () => {
  // TODO: This is kind of a hack to mimic a React-like state construct.
  // It should be removed once we have a real front-end framework in place.
  $(":input").each(function() {
    $(this).data("initial", $(this).val());
  });

  $(function() {
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

    bindMarkdownEditors();
    makeSortableTables();
    $('[data-toggle="tooltip"]').tooltip();
  });
};
