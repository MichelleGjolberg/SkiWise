// frontend/vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';
// import { vi } from 'vitest';
// import mapboxgl from 'mapbox-gl';


export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '~': path.resolve(__dirname, 'app'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './setupTests.ts',
    include: ['app/**/*.{test,spec}.{ts,tsx}'],
  },
});


// // Mock mapbox-gl
// vi.mock('mapbox-gl', () => {
//   return {
//     ...vi.importActual('mapbox-gl'),
//     Map: vi.fn().mockImplementation(() => ({
//       on: vi.fn(),
//       setStyle: vi.fn(),
//     })),
//   };
// });

