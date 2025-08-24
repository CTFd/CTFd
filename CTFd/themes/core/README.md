# core-beta

Rewritten version of the CTFd core theme to use Bootstrap 5, Alpine.js, and vite to improve upon the existing CTFd theme structure. 

## Subtree Installation

### Add repo to themes folder

```
git subtree add --prefix CTFd/themes/core-beta git@github.com:CTFd/core-beta.git main --squash
```

### Pull latest changes to subtree
```
git subtree pull --prefix CTFd/themes/core-beta git@github.com:CTFd/core-beta.git main --squash
```

### Subtree Gotcha

Make sure to use Merge Commits when dealing with the subtree here. For some reason Github's squash and commit uses the wrong line ending which causes issues with the subtree script: https://stackoverflow.com/a/47190256. 

## Creating Custom Theme (based on core-beta)

To create a custom theme based on the core-beta one, here are the steps to follow:

1. Clone core-beta theme locally to a seperate folder
   ```
   git clone https://github.com/CTFd/core-beta.git custom-theme
   ```
   To clarify the structure of the project, the `./assets` folder contains the uncompiled source files (the ones you can modify), while the `./static` directory contains the compiled ones. 

2. Install [Yarn](https://classic.yarnpkg.com/en/) following the [official installation guides](https://classic.yarnpkg.com/en/docs/install).
   * **Yarn** is a dependency management tool used to install and manage project packages
   * **[Vite](https://vite.dev/guide/)** handles the frontend tooling in CTFd by building optimized assets that are served through Flask.

4. Run `yarn install` in the root of `custom-theme` folder to install the necessary Node packages including `vite`.

5. Run the appropriate yarn build mode:
   - Run `yarn dev` (this will run `vite build --watch`) while developing the theme.
   - Run `yarn build` (which will run `vite build`) for a one-time build. 
   Vite allows you to preview changes instantly with hot reloading.


6. Now, you can start your modifications in the `assets` folder. Each time you save, Vite will automatically recompile everything (assuming you are using `yarn dev`), and you can directly see the result by importing your compiled theme into a CTFd instance.
   Note: You do not need the `node_modules` folder, you can simply zip the theme directory without it.

7. When you are ready you can use `yarn build` to build the production copy of your theme.

## Todo

- Document how we are using Vite
- Create a cookie cutter template package to use with Vite
