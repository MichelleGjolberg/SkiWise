// frontend/app/components/UserInput.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UserInput from '~/components/UserInput';
import { describe, it, expect } from 'vitest';

describe('UserInput component', () => {
  it('renders the form and allows typing a name', async () => {
    render(<UserInput />);

    const nameInput = screen.getByPlaceholderText('Enter your name');
    expect(nameInput).toBeInTheDocument();

    await userEvent.type(nameInput, 'Alice');
    expect(nameInput).toHaveValue('Alice');
  });
});
