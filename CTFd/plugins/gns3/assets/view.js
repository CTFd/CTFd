// /plugins/gns3/assets/view.js
// Attach click handler to the Run VM button
$(function(){
  $('#run-vm').click(function(){
    var projectId = $(this).data('project-id');
    if(projectId) {
      // Open the start URL in a new tab/window
      window.open('https://franciscoalves.pt/plugins/gns3_controller/start/' + projectId, '_blank');
    } else {
      alert('Project ID not set.');
    }
  });
});
