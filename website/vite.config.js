import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";

const root = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  base: "/mdxl/",
  plugins: [react(), tailwindcss()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(root, "index.html"),
        guide: resolve(root, "guide/index.html"),
        syntax: resolve(root, "syntax/index.html"),
        installation: resolve(root, "installation/index.html"),
        renderers: resolve(root, "renderers/index.html"),
        examples: resolve(root, "examples/index.html"),
        about: resolve(root, "about/index.html")
      }
    }
  }
});
