import { vitePlugin as remix } from "@remix-run/dev";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";
import { defineConfig } from "vitest/config";
import { installGlobals } from "@remix-run/node";

installGlobals();

const MODE = process.env.NODE_ENV;

declare module "@remix-run/node" {
  interface Future {
    v3_singleFetch: true;
  }
}

export default defineConfig({

  test: {
    include: ["**/__tests__/**.{js,jsx,ts,tsx}"],
    globals: true,
    environment: 'jsdom',
    setupFiles: './setupTests.ts',
    restoreMocks: true,
    // coverage: {
    //   exclude: ["**/__tests__/**"],
    //   include: ["app/**/*.{ts,tsx}"],
    //   all: true,
    // },
    alias: {
      "~": "/app",
    },
  },

  plugins: [
    remix({
      future: {
        v3_fetcherPersist: true,
        v3_relativeSplatPath: true,
        v3_throwAbortReason: true,
        v3_singleFetch: true,
        v3_lazyRouteDiscovery: true,
      },
    }),
    tsconfigPaths(),
  ],
});
