const { resolve } = require("path");
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import copy from "rollup-plugin-copy";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "~": resolve(__dirname, "./node_modules/"),
      core: resolve(__dirname, "../core/assets/js/"),
      vue: "@vue/compat"
    }
  },
  build: {
    manifest: "manifest.json",
    outDir: "static",
    rollupOptions: {
      plugins: [
        copy({
          targets: [
            // https://github.com/vitejs/vite/issues/1618#issuecomment-764579557
            {
              src: "./node_modules/@fortawesome/fontawesome-free/webfonts/**/*",
              dest: "static/webfonts",
            },
            {
              src: "./node_modules/@fontsource/lato/files/**/*400*-normal*",
              dest: "static/webfonts"
            },
            {
              src: "./node_modules/@fontsource/lato/files/**/*700*-normal*",
              dest: "static/webfonts"
            },
            {
              src: "./node_modules/@fontsource/raleway/files/**/*500*-normal*",
              dest: "static/webfonts"
            },
            {
              src: "./node_modules/@ctfdio/ctfd-js/assets/images/**",
              dest: "static/img"
            },
            {
              src: "./node_modules/@ctfdio/ctfd-js/assets/sounds/**",
              dest: "static/sounds"
            }
          ],
          hook: "writeBundle"
        })
      ],
      output: {
        manualChunks: {
          echarts: ["echarts", "zrender"]
        }
      },
      input: {
        "pages/main": resolve(__dirname, "assets/js/pages/main.js"),
        "pages/challenge": resolve(__dirname, "assets/js/pages/challenge.js"),
        "pages/challenges": resolve(__dirname, "assets/js/pages/challenges.js"),
        "pages/configs": resolve(__dirname, "assets/js/pages/configs.js"),
        "pages/notifications": resolve(
          __dirname,
          "assets/js/pages/notifications.js"
        ),
        "pages/editor": resolve(__dirname, "assets/js/pages/editor.js"),
        "pages/pages": resolve(__dirname, "assets/js/pages/pages.js"),
        "pages/reset": resolve(__dirname, "assets/js/pages/reset.js"),
        "pages/scoreboard": resolve(__dirname, "assets/js/pages/scoreboard.js"),
        "pages/statistics": resolve(__dirname, "assets/js/pages/statistics.js"),
        "pages/submissions": resolve(
          __dirname,
          "assets/js/pages/submissions.js"
        ),
        "pages/team": resolve(__dirname, "assets/js/pages/team.js"),
        "pages/teams": resolve(__dirname, "assets/js/pages/teams.js"),
        "pages/user": resolve(__dirname, "assets/js/pages/user.js"),
        "pages/users": resolve(__dirname, "assets/js/pages/users.js"),
        "main-css": resolve(__dirname, "assets/css/main.scss"),
        "fonts-css": resolve(__dirname, "assets/css/fonts.scss"),
        "admin-css": resolve(__dirname, "assets/css/admin.scss"),
        "codemirror-css": resolve(__dirname, "assets/css/codemirror.scss"),
        "challenge-board-css": resolve(
          __dirname,
          "assets/css/challenge-board.scss"
        )
      }
    }
  }
});
