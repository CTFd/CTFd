
// Set up a MutationObserver to watch for new challenge modal content
const observer = new MutationObserver(mutations => {
  for (let m of mutations) {
    for (let node of m.addedNodes) {
      if (node.nodeType !== 1) continue; // Skip non-element nodes

      // Find a new challenge tab pane
      const challengePane = node.querySelector?.('#challenge') || (node.id === 'challenge' ? node : null);
      if (challengePane && !challengePane.querySelector('#test-button')) {
        // Create the button
        const btn = document.createElement('button');
        btn.id = 'test-button';
        btn.className = 'btn btn-warning mt-3';
	btn.textContent = 'Run VM';

	btn.onclick = () => {
	  fetch("https://franciscoalves.pt/plugins/gns3_controller/start/a443fc73-e345-461c-9776-a71c4b5b2353")
	    .then(response => {
	      if (!response.ok) {
	        throw new Error(`Request failed with status ${response.status}`);
	      }
	      alert("Request sent successfully!");
	    })
	    .catch(error => {
	      alert("Error sending request: " + error.message);
	    });
	};

        // Insert it at the bottom (e.g., after tags or description)
        const target = challengePane.querySelector('.challenge-tags') || challengePane;
        target.appendChild(btn);
      }
    }
  }
});

// Start observing changes to the body subtree
observer.observe(document.body, { childList: true, subtree: true });
