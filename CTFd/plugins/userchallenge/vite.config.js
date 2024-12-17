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
      core: resolve(__dirname, "../../themes/core/assets/js/"),
      vue: "@vue/compat"
    }
  },
  build: {
    manifest: "manifest.json",
    outDir: "staticAssets",
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
        "js/main": resolve(__dirname, "assets/js/main.js"),
        "js/userChallenge": resolve(__dirname, "assets/js/userChallenge.js"),              
        "js/config" : resolve(__dirname,"assets/js/config.js"),
        "js/adminChallenges" : resolve(__dirname,"assets/js/adminChallenges.js")
      }
    }
  }
});
