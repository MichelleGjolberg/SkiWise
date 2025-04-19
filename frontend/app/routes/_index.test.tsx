import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Index from '~/routes/_index';
import { describe, it, expect, vi, beforeEach } from 'vitest';


// Mock components to isolate logic
vi.mock('~/components/UserInput', () => ({
  default: () => <div data-testid="user-input">Mocked UserInput</div>,
}));
vi.mock('~/components/NavBar', () => ({
  default: () => <nav>Mocked NavBar</nav>,
}));
vi.mock('~/components/Footer', () => ({
  default: () => <footer>Mocked Footer</footer>,
}));

describe('Index Page', () => {
  it('renders the welcome button and hides UserInput initially', () => {
    render(<Index />);
    expect(
      screen.getByRole('button', {
        name: /Welcome to Skiwise - Find your mountain/i,
      })
    ).toBeInTheDocument();
    expect(screen.queryByTestId('user-input')).not.toBeInTheDocument();
  });

  it('shows UserInput and disables the button after click', async () => {
    render(<Index />);
    const button = screen.getByRole('button');

    fireEvent.click(button);

    // Wait for state update
    await waitFor(() =>
      expect(screen.getByTestId('user-input')).toBeInTheDocument()
    );
    expect(button).toBeDisabled();
  });

  it('scrolls into view when clicking the button', async () => {
    const scrollIntoView = vi.fn();
    // Manually mock scrollIntoView on HTMLElement prototype
    window.HTMLElement.prototype.scrollIntoView = scrollIntoView;

    render(<Index />);
    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(scrollIntoView).toHaveBeenCalled();
    });
  });
});
