import { fireEvent, render, screen } from "@testing-library/react";

import { App } from "@/app/App";

describe("App", () => {
  it("renders the purchase request application shell and navigates back", () => {
    window.history.replaceState({}, "", "/requests/new");
    render(<App />);
    expect(screen.getByRole("heading", { name: "New Purchase Request", level: 1 })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Back to requests/ }));
    expect(screen.getByRole("heading", { name: "Purchase Requests", level: 1 })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/requests");
  });
});
