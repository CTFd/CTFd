const { resolve } = require("path");
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import copy from "rollup-plugin-copy";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "~": resolve(__dirname, "./node_modules/"),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        silenceDeprecations: ["import", "global-builtin", "color-functions"],
        quietDeps: true,
      },
    },
  },
  build: {
    chunkSizeWarningLimit: 600,
    manifest: "manifest.json",
    outDir: "static",
    rollupOptions: {
      plugins: [
        copy({
          targets: [
            {
              src: "./node_modules/@fortawesome/fontawesome-free/webfonts/*",
              dest: "static/webfonts",
            },
            {
              src: "./node_modules/@fontsource/jetbrains-mono/files/*400*-normal*",
              dest: "static/webfonts",
            },
            {
              src: "./node_modules/@fontsource/jetbrains-mono/files/*700*-normal*",
              dest: "static/webfonts",
            },
            {
              src: "./node_modules/@fontsource/jetbrains-mono/files/*500*-normal*",
              dest: "static/webfonts",
            },
            {
              src: "./assets/img/**",
              dest: "static/img",
            },
          ],
          hook: "writeBundle",
        }),
      ],
      output: {
        manualChunks: {
          echarts: ["echarts", "zrender"],
        },
      },
      input: {
        index: resolve(__dirname, "assets/js/index.js"),
        page: resolve(__dirname, "assets/js/page.js"),
        setup: resolve(__dirname, "assets/js/setup.js"),
        settings: resolve(__dirname, "assets/js/settings.js"),
        challenges: resolve(__dirname, "assets/js/challenges.js"),
        scoreboard: resolve(__dirname, "assets/js/scoreboard.js"),
        notifications: resolve(__dirname, "assets/js/notifications.js"),
        teams_public: resolve(__dirname, "assets/js/teams/public.js"),
        teams_private: resolve(__dirname, "assets/js/teams/private.js"),
        teams_list: resolve(__dirname, "assets/js/teams/list.js"),
        users_public: resolve(__dirname, "assets/js/users/public.js"),
        users_private: resolve(__dirname, "assets/js/users/private.js"),
        users_list: resolve(__dirname, "assets/js/users/list.js"),
        main: resolve(__dirname, "assets/scss/main.scss"),
      },
    },
  },
});
