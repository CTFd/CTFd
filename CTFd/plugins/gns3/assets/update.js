// /plugins/gns3/assets/update.js
// Populate the Project ID when editing an existing challenge
function openchal(id) {
  loadchal(id);  // Load standard fields into the modal
  setTimeout(function() {
    // `challengeData` is populated by loadchal(); we assume it includes project_id
    var projectId = challengeData.project_id || "";
    $('#update-challenge-modal').find('[name=project_id]').val(projectId);
  }, 250);
}
