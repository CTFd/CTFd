
// /plugins/gns3/assets/create.js
// (Optional initialization on the create modal, if needed)
$(function(){
  // When the create-challenge modal is shown, clear the Project ID field
  $('#add-challenge-modal').on('shown.bs.modal', function() {
    $(this).find('[name=project_id]').val('');
  });
});


project_id = request.form.get('project_id') or ""
chal.metadata = chal.metadata or {}
chal.metadata['project_id'] = project_id
