import { fireEvent, render, screen } from "@testing-library/react";

import { NewPurchaseRequest } from "@/features/requests/NewPurchaseRequest";

describe("NewPurchaseRequest", () => {
  it("validates plain-language request text", () => {
    render(<NewPurchaseRequest onBack={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("What do you want to purchase?"), { target: { value: "laptop" } });
    fireEvent.click(screen.getByRole("button", { name: /Submit Request/ }));
    expect(screen.getByText("Please provide more details (at least 10 characters).")).toBeInTheDocument();
  });

  it("keeps workflow submission honest until its backend boundary exists", () => {
    render(<NewPurchaseRequest onBack={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("What do you want to purchase?"), { target: { value: "I need two laptop stands" } });
    fireEvent.click(screen.getByRole("button", { name: /Submit Request/ }));
    expect(screen.getByText(/workflow submission will be connected/i)).toBeInTheDocument();
  });
});
