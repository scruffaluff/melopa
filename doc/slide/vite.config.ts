/**
 * Vite configuration file for building web projects.
 *
 * For more information, visit https://vitejs.dev/config.
 */

import { createReadStream, existsSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig, type Plugin } from "vite";

const publicDir = fileURLToPath(new URL("../public", import.meta.url));

// Serve shared public directory in dev mode and resolve paths during build so
// slides can use asset routes from the production layout.
//
// Uses "\0" convention to prevent other plugins from processing as explained at
// https://rolldown.rs/apis/plugin-api#virtual-modules.
function publicAssets(): Plugin {
  const prefix = "/melopa/";
  return {
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const url = request.url?.split("?")[0];
        if (url === undefined || !url.startsWith(prefix)) {
          next();
          return;
        }

        const file = fileURLToPath(
          new URL(
            `../public/${decodeURIComponent(url.slice(prefix.length))}`,
            import.meta.url
          )
        );
        if (
          !file.startsWith(publicDir) ||
          !existsSync(file) ||
          !statSync(file).isFile()
        ) {
          next();
          return;
        }
        createReadStream(file).pipe(response);
      });
    },
    load(id) {
      if (!id.startsWith("\0" + prefix)) {
        return;
      }
      return `export default ${JSON.stringify(id.slice(1))}`;
    },
    resolveId(id) {
      if (!id.startsWith(prefix)) {
        return;
      }
      const file = fileURLToPath(
        new URL(
          `../public/${decodeURIComponent(id.slice(prefix.length))}`,
          import.meta.url
        )
      );
      if (!file.startsWith(publicDir) || !existsSync(file)) {
        return;
      }
      return `\0${id}`;
    },
    name: "melopa:public-assets",
  };
}

export default defineConfig({
  build: {
    emptyOutDir: true,
  },
  plugins: [publicAssets()],
});
