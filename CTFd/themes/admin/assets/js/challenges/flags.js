import $ from "jquery";
import CTFd from "core/CTFd";
import nunjucks from "nunjucks";
import { ezQuery } from "core/ezq";
import Vue from "vue/dist/vue.esm.browser";
import FlagCreationForm from "../components/flags/FlagCreationForm.vue";

export function deleteFlag(event) {
  event.preventDefault();
  const flag_id = $(this).attr("flag-id");
  const row = $(this)
    .parent()
    .parent();

  ezQuery({
    title: "Delete Flag",
    body: "Are you sure you want to delete this flag?",
    success: function() {
      CTFd.fetch("/api/v1/flags/" + flag_id, {
        method: "DELETE"
      })
        .then(function(response) {
          return response.json();
        })
        .then(function(response) {
          if (response.success) {
            row.remove();
          }
        });
    }
  });
}

export function addFlagModal(_event) {
  const flagCreationForm = Vue.extend(FlagCreationForm);

  let vueContainer = document.createElement("div");
  document.querySelector("main").appendChild(vueContainer);

  let f = new flagCreationForm({
    propsData: { challenge_id: window.CHALLENGE_ID }
  }).$mount(vueContainer);

  $("#flag-create-modal").on("hidden.bs.modal", function (_e) {
    f.$destroy();
    $("#flag-create-modal").remove();
  });

  $("#flag-create-modal").modal();
}

export function editFlagModal(event) {
  event.preventDefault();
  const flag_id = $(this).attr("flag-id");
  const row = $(this)
    .parent()
    .parent();

  $.get(CTFd.config.urlRoot + "/api/v1/flags/" + flag_id, function(response) {
    const data = response.data;
    $.get(CTFd.config.urlRoot + data.templates.update, function(template_data) {
      $("#edit-flags form").empty();
      $("#edit-flags form").off();

      const template = nunjucks.compile(template_data);
      $("#edit-flags form").append(template.render(data));

      $("#edit-flags form").submit(function(event) {
        event.preventDefault();
        const params = $("#edit-flags form").serializeJSON();

        CTFd.fetch("/api/v1/flags/" + flag_id, {
          method: "PATCH",
          credentials: "same-origin",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify(params)
        })
          .then(function(response) {
            return response.json();
          })
          .then(function(response) {
            if (response.success) {
              $(row)
                .find(".flag-content")
                .text(response.data.content);
              $("#edit-flags").modal("toggle");
            }
          });
      });
      $("#edit-flags").modal();
    });
  });
}
