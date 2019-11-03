import "./main";
import "../utils";
import $ from "jquery";
import CTFd from "../CTFd";
import { ezAlert, ezQuery } from "../ezq";

const error_template =
  '<div class="alert alert-danger alert-dismissable" role="alert">\n' +
  '  <span class="sr-only">Error:</span>\n' +
  "  {0}\n" +
  '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>\n' +
  "</div>";

const success_template =
  '<div class="alert alert-success alert-dismissable submit-row" role="alert">\n' +
  "  <strong>Success!</strong>\n" +
  "   Your profile has been updated\n" +
  '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button>\n' +
  "</div>";

function profileUpdate(event) {
  event.preventDefault();
  $("#results").empty();
  const $form = $(this);
  let params = $form.serializeJSON(true);

  // Special case country to allow for removals
  params.country = $form.serializeJSON(false)["country"];

  CTFd.api.patch_user_private({}, params).then(response => {
    if (response.success) {
      $("#results").html(success_template);
    } else if ("errors" in response) {
      Object.keys(response.errors).map(function(error) {
        const i = $form.find("input[name={0}]".format(error));
        const input = $(i);
        input.addClass("input-filled-invalid");
        input.removeClass("input-filled-valid");
        const error_msg = response.errors[error];
        $("#results").append(error_template.format(error_msg));
      });
    }
  });
}

function tokenGenerate(event) {
  event.preventDefault();
  const $form = $(this);
  let params = $form.serializeJSON(true);

  CTFd.fetch("/api/v1/tokens", {
    method: "POST",
    body: JSON.stringify(params)
  })
    .then(function(response) {
      return response.json();
    })
    .then(function(response) {
      if (response.success) {
        ezAlert({
          title: "API Key Generated",
          body: `Please copy your API Key, it won't be shown again! <br><br> <code>${
            response.data.value
          }</code>`,
          button: "Got it!",
          large: true
        });
      }
    });
}

function deleteToken(event) {
  event.preventDefault();
  const $elem = $(this);
  const id = $elem.data("token-id");

  ezQuery({
    title: "Delete Token",
    body: "Are you sure you want to delete this token?",
    success: function() {
      CTFd.fetch("/api/v1/tokens/" + id, {
        method: "DELETE"
      })
        .then(function(response) {
          return response.json();
        })
        .then(function(response) {
          if (response.success) {
            $elem
              .parent()
              .parent()
              .remove();
          }
        });
    }
  });
}

$(() => {
  $("#user-profile-form").submit(profileUpdate);
  $("#user-token-form").submit(tokenGenerate);
  $(".delete-token").click(deleteToken);
});
