// app/components/__tests__/NavBar.test.tsx
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import NavBar from '~/components/NavBar';
import { describe, it, expect } from 'vitest';


describe('NavBar', () => {
  it('renders the SkiWise logo and link', () => {
    render(
      <MemoryRouter>
        <NavBar />
      </MemoryRouter>
    );

    // Text content
    expect(screen.getByText('SkiWise')).toBeInTheDocument();

    // Image alt text
    expect(screen.getByAltText('SkiWise Logo')).toBeInTheDocument();

    // Link check
    const link = screen.getByRole('link', { name: /skiwise/i });
    expect(link).toHaveAttribute('href', '/');
  });
});
