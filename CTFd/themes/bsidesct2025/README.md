# BSides Connecticut 2025 - "They Live" CTF Theme

A custom CTFd theme inspired by John Carpenter's "They Live" (1988) for BSides Connecticut 2025.

## Theme Features

- **Retro Terminal Aesthetic**: Monospace fonts, green-on-black color scheme
- **Interactive Sunglasses Effect**: Toggle button to reveal hidden messages
- **Scanlines Animation**: Continuous CRT-style scanlines overlay
- **Glitch Effects**: Random glitch animations on headings
- **Hidden Messages**: Secret text revealed only with "sunglasses" mode
- **Terminal Styling**: Command-line inspired UI elements
- **High Contrast**: Black/white/green color palette for maximum impact

## Installation & Build

### Install Dependencies
```bash
npm install
```

### Development (with file watching)
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

## Theme Elements

### Color Palette
- Primary: Black (#000000)
- Secondary: White (#ffffff) 
- Accent: Neon Green (#00ff00)
- Alert: Red (#ff0000)

### Interactive Features
- **Sunglasses Toggle**: Click the 🕶️ button to reveal hidden messages
- **Glitch Effects**: Headings randomly glitch every few seconds
- **Terminal Cursors**: Input fields show blinking terminal cursors when focused
- **Scanlines**: Animated CRT-style overlay effect

### Typography
- All text uses monospace fonts (Courier New, Monaco, Menlo)
- Uppercase styling for headings and buttons
- Terminal-style prompts and messages

## Customization

The theme is built with Bootstrap 5 and uses SCSS for styling. Key files:

- `assets/scss/includes/they-live/_variables.scss` - Color and typography variables
- `assets/scss/includes/they-live/_effects.scss` - Animation and visual effects
- `assets/scss/includes/they-live/_components.scss` - Component styling
- `assets/js/they-live.js` - Interactive JavaScript features

## Based on CTFd core-beta

This theme extends the CTFd core-beta theme with Bootstrap 5, Alpine.js, and Vite build system.
