// frontend/vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '~': path.resolve(__dirname, 'app'), // relative to frontend
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    // setupFiles: './vitest.setup.ts',
    include: ['app/**/*.{test,spec}.{ts,tsx}'],
  },
});
