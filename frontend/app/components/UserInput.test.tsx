// frontend/app/components/UserInput.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UserInput from '~/components/UserInput';
import { describe, it, expect, vi } from 'vitest';



describe('UserInput component', () => {
  it('renders the form and allows typing a name', async () => {
    render(<UserInput />);

    const nameInput = screen.getByPlaceholderText('Enter your name');
    expect(nameInput).toBeInTheDocument();

    await userEvent.type(nameInput, 'Alice');
    expect(nameInput).toHaveValue('Alice');
  });
});

import mapboxgl from 'mapbox-gl';
// import { vi } from 'vitest';


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
