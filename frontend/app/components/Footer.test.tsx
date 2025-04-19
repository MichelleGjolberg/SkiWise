// app/components/__tests__/Footer.test.tsx
import { render, screen } from '@testing-library/react';
import Footer from '~/components/Footer';
import { describe, it, expect } from 'vitest';

describe('Footer', () => {
  it('renders the current year and SkiWise text', () => {
    render(<Footer />);
    
    const currentYear = new Date().getFullYear();
    expect(
      screen.getByText(`© ${currentYear} SkiWise. All rights reserved.`)
    ).toBeInTheDocument();
  });
});
