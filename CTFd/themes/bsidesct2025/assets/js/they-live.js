// They Live Interactive Effects
document.addEventListener('DOMContentLoaded', function() {
    // Add scanlines effect
    const scanlines = document.createElement('div');
    scanlines.className = 'scanlines';
    document.body.appendChild(scanlines);
    
    // Sunglasses toggle
    let sunglassesMode = false;
    const sunglassesToggle = document.createElement('button');
    sunglassesToggle.innerHTML = '🕶️ PUT ON GLASSES';
    sunglassesToggle.className = 'btn btn-primary position-fixed';
    sunglassesToggle.style.cssText = 'top: 20px; right: 20px; z-index: 1001; font-size: 12px;';
    
    sunglassesToggle.addEventListener('click', function() {
        sunglassesMode = !sunglassesMode;
        document.body.classList.toggle('sunglasses-view', sunglassesMode);
        this.innerHTML = sunglassesMode ? '🕶️ REMOVE GLASSES' : '🕶️ PUT ON GLASSES';
        
        // Reveal hidden messages
        document.querySelectorAll('.hidden-message').forEach(el => {
            el.classList.toggle('revealed', sunglassesMode);
        });
    });
    
    document.body.appendChild(sunglassesToggle);
    
    // Random glitch effect on headings
    setInterval(() => {
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        if (headings.length > 0 && Math.random() < 0.1) {
            const randomHeading = headings[Math.floor(Math.random() * headings.length)];
            randomHeading.classList.add('glitch');
            setTimeout(() => randomHeading.classList.remove('glitch'), 300);
        }
    }, 2000);
    
    // Add terminal cursor to inputs when focused
    document.querySelectorAll('input[type="text"], input[type="password"], textarea').forEach(input => {
        input.addEventListener('focus', () => input.classList.add('terminal-cursor'));
        input.addEventListener('blur', () => input.classList.remove('terminal-cursor'));
    });
    
    // Hidden messages that appear with sunglasses
    const hiddenMessages = [
        'THEY CONTROL THE FLAGS',
        'WAKE UP',
        'QUESTION EVERYTHING',
        'THE TRUTH IS IN THE CODE'
    ];
    
    // Add hidden messages to random locations
    setTimeout(() => {
        hiddenMessages.forEach((msg, index) => {
            const hiddenEl = document.createElement('div');
            hiddenEl.className = 'hidden-message position-fixed';
            hiddenEl.textContent = msg;
            hiddenEl.style.cssText = `
                top: ${20 + index * 100}px; 
                left: ${Math.random() * 50 + 10}%; 
                z-index: 999; 
                font-size: 14px; 
                font-weight: bold;
                pointer-events: none;
            `;
            document.body.appendChild(hiddenEl);
        });
    }, 1000);
});
