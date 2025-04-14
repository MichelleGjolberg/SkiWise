// // frontend/app/components/UserInput.test.tsx
// import { render, screen, waitFor } from '@testing-library/react';
// import userEvent from '@testing-library/user-event';
// import UserInput from '~/components/UserInput';
// import { describe, it, expect, vi, beforeEach } from 'vitest';

// // // Mock geolocation
// // beforeEach(() => {
// //   vi.stubGlobal('navigator', {
// //     geolocation: {
// //       getCurrentPosition: vi.fn((success) =>
// //         success({ coords: { latitude: 40, longitude: -105 } })
// //       ),
// //     },
// //   });

// //   // Mock fetch
// //   global.fetch = vi.fn(() =>
// //     Promise.resolve({
// //       ok: true,
// //       json: () => Promise.resolve({ success: true }),
// //     })
// //   ) as any;
// // });

// describe('UserInput component', () => {
//   it('renders the form and allows typing a name', async () => {
//     render(<UserInput />);
//     // describe('UserInput component full test', () => {
//     //   it('fills the form and submits', async () => {
//     //     render(<UserInput />);
//     // const user = userEvent.setup();

//     const nameInput = screen.getByPlaceholderText('Enter your name');
//     expect(nameInput).toBeInTheDocument();

//     await userEvent.type(nameInput, 'Alice');
//     expect(nameInput).toHaveValue('Alice');
//   });
// });


// // Mock mapbox-gl
// vi.mock('mapbox-gl', async () => {
//   const actual = await import('mapbox-gl');
//   return {
//     ...actual,
//     default: {
//       ...actual.default,
//       Map: vi.fn().mockImplementation(() => ({
//         on: vi.fn(),
//         setStyle: vi.fn(),
//         remove: vi.fn(), // Add mock for remove method
//       })),
//     },
//   };
// });

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UserInput from '~/components/UserInput';
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock geolocation
beforeEach(() => {
  vi.stubGlobal('navigator', {
    geolocation: {
      getCurrentPosition: vi.fn((success) =>
        success({ coords: { latitude: 40, longitude: -105 } })
      ),
    },
  });

  // Mock fetch
  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    })
  ) as any;
});

// Test when geolocation is available
describe('UserInput component with geolocation', () => {
  it('should use geolocation when available', async () => {
    // Mock successful geolocation response
    const getCurrentPositionMock = vi.fn((success) =>
      success({ coords: { latitude: 40, longitude: -105 } })
    );
    vi.stubGlobal('navigator', {
      geolocation: {
        getCurrentPosition: getCurrentPositionMock,
      },
    });

    const sendFormData = vi.fn(); // Mock sendFormData function
    render(<UserInput sendFormData={sendFormData} />);

    const submitBtn = screen.getByRole('button', { name: /find your mountain/i });

    await userEvent.click(submitBtn);

    await waitFor(() => {
      // Ensure geolocation was called
      expect(getCurrentPositionMock).toHaveBeenCalled();

      // Check that sendFormData was called with the correct coordinates
      expect(sendFormData).toHaveBeenCalledWith(40, -105); // Mocked geolocation coordinates
    });
  });

  it('should use default location if geolocation fails', async () => {
    // Mock geolocation error
    const getCurrentPositionMock = vi.fn((success, error) =>
      error(new Error('Geolocation error'))
    );
    vi.stubGlobal('navigator', {
      geolocation: {
        getCurrentPosition: getCurrentPositionMock,
      },
    });

    const sendFormData = vi.fn(); // Mock sendFormData function
    render(<UserInput sendFormData={sendFormData} />);

    const submitBtn = screen.getByRole('button', { name: /find your mountain/i });

    await userEvent.click(submitBtn);

    await waitFor(() => {
      // Ensure geolocation error handler was triggered
      expect(getCurrentPositionMock).toHaveBeenCalled();

      // Check that sendFormData was called with the default coordinates
      expect(sendFormData).toHaveBeenCalledWith(40.0189728, -105.2747406); // Default Boulder, CO
    });
  });

  it('should log an error when geolocation is not supported', async () => {
    // Simulate no geolocation support
    vi.stubGlobal('navigator', {
      geolocation: undefined, // Geolocation is not supported
    });

    const consoleErrorMock = vi.spyOn(console, 'error').mockImplementation(() => {});

    const sendFormData = vi.fn(); // Mock sendFormData function
    render(<UserInput sendFormData={sendFormData} />);

    const submitBtn = screen.getByRole('button', { name: /find your mountain/i });

    await userEvent.click(submitBtn);

    await waitFor(() => {
      // Check that the error message is logged when geolocation is not supported
      expect(consoleErrorMock).toHaveBeenCalledWith('Geolocation is not supported by this browser.');
    });

    consoleErrorMock.mockRestore();
  });
});


describe('UserInput component full user input test', () => {
  it('fills the form and submits', async () => {
    render(<UserInput />);
    const user = userEvent.setup();

    // Fill basic inputs
    await user.type(screen.getByPlaceholderText('Enter your name'), 'Alice');
    await user.type(screen.getByPlaceholderText('Enter driving time'), '60');
    await user.type(screen.getByPlaceholderText('Enter number of people'), '4');
    await user.type(screen.getByPlaceholderText('Enter your budget'), '300');
    await user.type(screen.getByPlaceholderText('Enter inches of fresh snow'), '5');

    // Select driving experience
    await user.selectOptions(screen.getByDisplayValue('Beginner'), 'intermediate');
    expect(screen.getByDisplayValue('Intermediate')).toBeInTheDocument();

    // Select pass type
    await user.click(screen.getByLabelText('Epic Pass'));


    const costSlider = screen.getByLabelText(/how important is cost/i);
    const timeSlider = screen.getByLabelText(/how important is driving time/i);
    await userEvent.type(costSlider, '{arrowRight}{arrowRight}');
    await userEvent.type(timeSlider, '{arrowLeft}');


    // Submit form
    const submitBtn = screen.getByRole('button', { name: /find your mountain/i });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/get_mountain',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });
  });


  describe('UserInput validation errors', () => {
    it('shows budgetError when budget is 0 or less', () => {
      render(<UserInput />);
  
      fireEvent.change(screen.getByPlaceholderText('Enter your name'), {
        target: { value: 'John' },
      });
      fireEvent.change(screen.getByPlaceholderText('Enter driving time'), {
        target: { value: '30' },
      });
      fireEvent.change(screen.getByPlaceholderText('Enter number of people'), {
        target: { value: '2' },
      });
      fireEvent.change(screen.getByPlaceholderText('Enter your budget'), {
        target: { value: '0' },
      });
  
      fireEvent.click(screen.getByText('Find your mountain'));
  
      expect(screen.getByText('Budget should be > 0 dollars')).toBeInTheDocument();
    });
  
    it('shows distanceError when driving time is 0 or less', () => {
      render(<UserInput />);
  
      fireEvent.change(screen.getByPlaceholderText('Enter your name'), {
        target: { value: 'John' },
      });
      fireEvent.change(screen.getByPlaceholderText('Enter driving time'), {
        target: { value: '0' },
      });
      fireEvent.change(screen.getByPlaceholderText('Enter number of people'), {
        target: { value: '2' },
      });
      fireEvent.change(screen.getByPlaceholderText('Enter your budget'), {
        target: { value: '200' },
      });
  
      fireEvent.click(screen.getByText('Find your mountain'));
  
      expect(screen.getByText('Driving time should be > 0 minutes')).toBeInTheDocument();
    });
  
    it('shows peopleError when number of people is 0 or less', () => {
      render(<UserInput />);
  
      fireEvent.change(screen.getByPlaceholderText('Enter your name'), {
        target: { value: 'John' },
      });
      fireEvent.change(screen.getByPlaceholderText('Enter driving time'), {
        target: { value: '30' },
      });
      fireEvent.change(screen.getByPlaceholderText('Enter number of people'), {
        target: { value: '0' },
      });
      fireEvent.change(screen.getByPlaceholderText('Enter your budget'), {
        target: { value: '200' },
      });
  
      fireEvent.click(screen.getByText('Find your mountain'));
  
      expect(screen.getByText('Number of people should be > 0')).toBeInTheDocument();
    });
  });
});

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
