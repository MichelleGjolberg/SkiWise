import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { it, expect, describe } from 'vitest';
import UserInput from "../../app/components/UserInput";

describe("UserInput Component", () => {
  it("shows an error when required fields are empty and the form is submitted", async () => {
    render(<UserInput/>);
    
    // Click the submit button without filling in the required fields
    fireEvent.click(screen.getByRole("button", { name: /find your mountain/i }));

    // Expect error message to be shown
    expect(await screen.findByText(/please fill out this field/i)).toBeInTheDocument();
  });
});
