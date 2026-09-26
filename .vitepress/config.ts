// VitePress documentation configuration file.
//
// This configuration uses the default VitePress theme, whose details can be
// found at https://vitepress.dev/reference/default-theme-config. For more
// information on VitePress configuration, visit
// https://vitepress.dev/reference/site-config.

import { fileURLToPath, URL } from "node:url";
import { marimoVitePress } from "@marimo-team/mdx-marimo/vitepress";
import { defineConfig } from "vitepress";
import { generateSidebar } from "vitepress-sidebar";

export default defineConfig({
  base: "/melopa/",
  description: "Scruffaluff wiki with tutorials, webapps, and workbooks.",
  // Head contents follow the progressive webapp requirements specified at
  // https://vite-pwa-org.netlify.app/guide/pwa-minimal-requirements.html.
  head: [
    ["link", { href: "/melopa/apple-touch-icon.png", rel: "apple-touch-icon" }],
    ["link", { href: "/melopa/favicon.ico", rel: "icon", sizes: "48x48" }],
    [
      "link",
      {
        href: "/melopa/favicon.svg",
        rel: "icon",
        sizes: "any",
        type: "image/svg+xml",
      },
    ],
    ["link", { href: "/melopa/site.webmanifest", rel: "manifest" }],
  ],
  ignoreDeadLinks: true,
  lastUpdated: true,
  markdown: {
    config: (md) => {
      // Prevent Shiki warnings about unknown marimo-config language. VitePress
      // search index encounters the warning since it renders Markdown outside
      // of the transform pipeline. Warning is avoided by removing the fence
      // which is safe since marimoVitePress also removes the fence during
      // builds.
      md.core.ruler.after("block", "marimo-config-to-txt", (state) => {
        for (const token of state.tokens) {
          if (token.type === "fence" && token.info.trim() === "marimo-config") {
            token.info = "";
          }
        }
      });
    },
    math: true,
  },
  outDir: "build/site",
  srcDir: "doc/site",
  themeConfig: {
    aside: false,
    footer: {
      message: "Released under the MIT License.",
      copyright: "Copyright © 2023-Present Macklan Weinstein",
    },
    nav: [
      { text: "Home", link: "/" },
      { text: "Audio", link: "/audio/" },
      { text: "Computing", link: "/compute/" },
      { text: "Mathematics", link: "/math/" },
      { text: "Notebooks", link: "/note/" },
      { text: "Slides", link: "/slide/" },
    ],
    search: {
      provider: "local",
    },
    sidebar: generateSidebar([
      {
        documentRootPath: "doc/site",
        resolvePath: "/audio/",
        scanStartPath: "audio",
        useTitleFromFileHeading: true,
      },
      {
        documentRootPath: "doc/site",
        resolvePath: "/compute/",
        scanStartPath: "compute",
        useTitleFromFileHeading: true,
      },
      {
        documentRootPath: "doc/site",
        resolvePath: "/math/",
        scanStartPath: "math",
        useTitleFromFileHeading: true,
      },
    ]),
    socialLinks: [
      { icon: "github", link: "https://github.com/scruffaluff/melopa" },
    ],
  },
  title: "Melopa",
  vite: {
    build: {
      // Marimo notebooks embed island payloads that require larger chunk sizes.
      chunkSizeWarningLimit: 4096,
    },
    publicDir: "../public",
    plugins: [marimoVitePress()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("../../src", import.meta.url)),
      },
    },
  },
  vue: {
    template: {
      compilerOptions: {
        isCustomElement: (tag) => ["marimo-mdx-island"].includes(tag),
      },
    },
  },
});
