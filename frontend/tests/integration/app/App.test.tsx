import { render, screen } from "@testing-library/react";

import { App } from "@/app/App";

describe("App", () => {
  it("renders the purchase request application shell", () => {
    window.history.replaceState({}, "", "/requests/new");
    render(<App />);
    expect(screen.getByRole("heading", { name: "New Purchase Request", level: 1 })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Back to requests/ })).toBeInTheDocument();
  });
});
