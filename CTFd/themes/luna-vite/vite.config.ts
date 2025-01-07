import { defineConfig } from 'vite';
import { resolve } from "path";
// import vue from '@vitejs/plugin-vue';
import copy from "rollup-plugin-copy";
import { CSSManifestPlugin } from "vite-manifest-css";

// https://vitejs.dev/config/
export default defineConfig({
  // mode: "development",
  plugins: [
    // vue(),
    // CSSManifestPlugin()
  ],
  resolve: {
    alias: {
      "~": resolve(__dirname, "./node_modules/"),
    },
  },
  build: {
    manifest: true,
    outDir: "static",
    rollupOptions: {
      plugins: [
        copy({
          targets: [
            // https://github.com/vitejs/vite/issues/1618#issuecomment-764579557
            // {
            //   src: "./node_modules/@fortawesome/fontawesome-free/webfonts/**/*",
            //   dest: "static/webfonts",
            // },
            // {
            //   src: "./node_modules/@fontsource/lato/files/**/*400*",
            //   dest: "static/webfonts",
            // },
            // {
            //   src: "./node_modules/@fontsource/raleway/files/**/*400*",
            //   dest: "static/webfonts",
            // },
            {
              src: "./assets/img/**/*",
              dest: "static/img",
            },
            {
              src: "./assets/sounds/**/*",
              dest: "static/sounds",
            },
            {
              src: "./assets/fonts/**/*",
              dest: "static/fonts",
            },
          ],
          hook: "writeBundle",
        }),
      ],
      output: {
        manualChunks: {
          echarts: ['echarts', 'zrender']
        }
      },
      input: {
        base: resolve(__dirname, "assets/js/base.js"),
        index: resolve(__dirname, "assets/js/index.js"),
        settings: resolve(__dirname, "assets/js/settings.js"),
        user_profile: resolve(__dirname, "assets/js/userProfile.js"),
        team_profile: resolve(__dirname, "assets/js/teamProfile.js"),
        team_admin: resolve(__dirname, "assets/js/teamAdmin.js"),
        scoreboard: resolve(__dirname, "assets/js/scoreboard.js"),
        notifications: resolve(__dirname, "assets/js/notifications.js"),
        challenges: resolve(__dirname, "assets/js/challenges.js"),
        // page: resolve(__dirname, "assets/js/page.js"),
        // setup: resolve(__dirname, "assets/js/setup.js"),
        main: resolve(__dirname, "assets/scss/main.scss"),
      },
    },
  },
})
