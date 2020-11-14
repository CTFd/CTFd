import $ from "jquery";
import CTFd from "core/CTFd";
import { ezQuery } from "core/ezq";
import Vue from "vue/dist/vue.esm.browser";
import FlagCreationForm from "../components/flags/FlagCreationForm.vue";
import FlagEditForm from "../components/flags/FlagEditForm.vue";

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

  $("#flag-create-modal").on("hidden.bs.modal", function(_e) {
    f.$destroy();
    $("#flag-create-modal").remove();
  });

  $("#flag-create-modal").modal();
}

export function editFlagModal(_event) {
  let flag_id = parseInt($(this).attr("flag-id"));
  const flagEditForm = Vue.extend(FlagEditForm);

  let vueContainer = document.createElement("div");
  document.querySelector("main").appendChild(vueContainer);

  let f = new flagEditForm({
    propsData: { flag_id: flag_id }
  }).$mount(vueContainer);

  $("#flag-edit-modal").on("hidden.bs.modal", function(_e) {
    f.$destroy();
    $("#flag-edit-modal").remove();
  });

  $("#flag-edit-modal").modal();
}
