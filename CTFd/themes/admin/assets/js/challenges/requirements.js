import $ from "jquery";
import CTFd from "core/CTFd";

export function addRequirement(event) {
  event.preventDefault();
  const requirements = $("#prerequisite-add-form").serializeJSON();

  // Shortcut if there's no prerequisite
  if (!requirements["prerequisite"]) {
    return;
  }

  window.CHALLENGE_REQUIREMENTS.prerequisites.push(
    parseInt(requirements["prerequisite"])
  );

  const params = {
    requirements: window.CHALLENGE_REQUIREMENTS
  };

  CTFd.fetch("/api/v1/challenges/" + window.CHALLENGE_ID, {
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
    .then(function(data) {
      if (data.success) {
        // TODO: Make this refresh requirements
        window.location.reload();
      }
    });
}

export function deleteRequirement(_event) {
  const challenge_id = $(this).attr("challenge-id");
  const row = $(this)
    .parent()
    .parent();

  window.CHALLENGE_REQUIREMENTS.prerequisites.pop(challenge_id);

  const params = {
    requirements: window.CHALLENGE_REQUIREMENTS
  };
  CTFd.fetch("/api/v1/challenges/" + window.CHALLENGE_ID, {
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
    .then(function(data) {
      if (data.success) {
        row.remove();
      }
    });
}
