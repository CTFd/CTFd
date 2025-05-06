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
        btn.className = 'btn btn-primary mt-3';
        btn.textContent = 'Test';

        btn.onclick = () => alert('Test button clicked!');

        // Insert it at the bottom (e.g., after tags or description)
        const target = challengePane.querySelector('.challenge-tags') || challengePane;
        target.appendChild(btn);
      }
    }
  }
});

// Start observing changes to the body subtree
observer.observe(document.body, { childList: true, subtree: true });
