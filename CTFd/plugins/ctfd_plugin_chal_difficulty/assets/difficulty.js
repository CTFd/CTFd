document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname !== '/challenges') return;

  fetch('/api/v1/difficulties')
    .then(response => response.json())
    .then(data => {
      if (!data.success) return;
      const entries = data.entries;
      const no_difficulties = parseInt(data.no_difficulties) || 0;

      const createBarContainer = (activeBars, isModal = false) => {
        const container = document.createElement('div');
        container.className = 'diff-container d-flex justify-content-center';

        if (isModal) {
          container.classList.add('mt-3', 'mb-4');
          container.style.width = '50%';
        } else {
          container.classList.add('mt-2');
          container.style.width = '80%';
        }

        container.style.gap = '4px';
        container.style.margin = '0 auto';

        for (let i = 0; i < no_difficulties; i++) {
          const bar = document.createElement('div');

          bar.style.flex = '1 1 auto';
          bar.style.maxWidth = isModal ? '20px' : '14px';
          bar.style.height = isModal ? '8px' : '6px';
          bar.style.borderRadius = '2px';

          if (i < activeBars) {
            if (i < no_difficulties / 3) { // first third
              bar.style.backgroundColor = '#00ff9d'; // green

            } else if (i < (no_difficulties * 2) / 3) { // second third
              bar.style.backgroundColor = '#ffc107'; // yellow

            } else { // last third
              bar.style.backgroundColor = '#ff4d4d'; // red
            }

          } else {
            bar.style.backgroundColor = 'rgba(128, 128, 128, 0.3)';
          }

          container.appendChild(bar);
        }
        return container;
      };

      const injectDifficultyBars = () => {

        // attempt to inject to challenge buttons
        // core theme: button.challenge-button (id in value)
        // modern theme: div.challenge-card-matrix (id in data-challenge-id)
        const challengeButtons = document.querySelectorAll('.challenge-button, .challenge-card-matrix[data-challenge-id]');
        challengeButtons.forEach(btn => {
          if (btn.querySelector('.diff-container')) return;

          const chalId = btn.value || btn.dataset.challengeId;
          const activeBars = parseInt(entries[chalId]) || 0;

          if (activeBars > 0) {
            const container = createBarContainer(activeBars, false);
            const target = btn.querySelector('.card-content') || btn;
            target.appendChild(container);
          }
        });

        // attempt to inject to challenge modals
        const chalIdInput = document.querySelector('#challenge-id');
        const chalDesc = document.querySelector('.challenge-desc')
                      || document.querySelector('.challenge-description');

        if (chalIdInput && chalDesc) {
          const modalChalId = chalIdInput.value;
          const activeBars = parseInt(entries[modalChalId]) || 0;

          let existingModalBars = document.querySelector('#modal-diff-bars');

          if (existingModalBars && existingModalBars.dataset.chalId !== modalChalId) {
            existingModalBars.remove();
            existingModalBars = null;
          }

          if (!existingModalBars && activeBars > 0) {
            const container = createBarContainer(activeBars, true);
            container.id = 'modal-diff-bars';
            container.dataset.chalId = modalChalId;

            chalDesc.parentNode.insertBefore(container, chalDesc);
          }
        }
      };

      injectDifficultyBars();

      const observer = new MutationObserver(injectDifficultyBars);
      observer.observe(document.body, { childList: true, subtree: true });
    })
    .catch(console.error);
});
