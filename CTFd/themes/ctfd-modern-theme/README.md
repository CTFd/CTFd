# CTFd Core Beta Theme

A modern CTFd theme built with Bootstrap 5, Alpine.js, and Vite.

## Features

- Modern UI with Bootstrap 5
- Alpine.js for reactive components
- Vite for fast development and optimized builds
- Dark mode support
- Responsive design
- ECharts integration for data visualization

## Installation

### Using Git Subtree

Add this theme to your CTFd installation:

```bash
git subtree add --prefix CTFd/themes/core-beta git@github.com:CTFd/core-beta.git main --squash
```

### Pull Latest Changes

```bash
git subtree pull --prefix CTFd/themes/core-beta git@github.com:CTFd/core-beta.git main --squash
```

## Development

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Setup

```bash
npm install
```

### Development Mode

Watch for changes and rebuild automatically:

```bash
npm run dev
```

### Build

Build for production:

```bash
npm run build
```

### Code Formatting

Format code:

```bash
npm run format
```

### Linting

Check code formatting:

```bash
npm run lint
```

## Project Structure

```
assets/
  js/          # JavaScript source files
  scss/         # SCSS stylesheets
  img/          # Image assets
templates/      # Jinja2 HTML templates
static/         # Built assets (generated)
```

## Technologies

- **Bootstrap 5**: UI framework
- **Alpine.js**: Lightweight JavaScript framework
- **Vite**: Build tool and dev server
- **ECharts**: Data visualization library
- **Sass**: CSS preprocessor

## License

See LICENSE file for details.
