// vitest.setup.ts
import '@testing-library/jest-dom';

import mapboxgl from 'mapbox-gl';
import { vi } from 'vitest';

// Mock mapbox-gl
vi.mock('mapbox-gl', async () => {
  const actual = await import('mapbox-gl');
  return {
    ...actual,
    default: {
      ...actual.default,
      Map: vi.fn().mockImplementation(() => ({
        on: vi.fn(),
        setStyle: vi.fn(),
        remove: vi.fn(), // Add mock for remove method
      })),
    },
  };
});

