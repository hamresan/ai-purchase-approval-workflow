import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { App } from "@/app/App";

describe("App", () => {
  it("renders the purchase request application shell and navigates back", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ items: [], total: 0, limit: 7, offset: 0 }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    window.history.replaceState({}, "", "/requests/new");

    render(<App />);
    expect(
      screen.getByRole("heading", { name: "New Purchase Request", level: 1 }),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Back to requests/ }));

    expect(
      screen.getByRole("heading", { name: "Purchase Requests", level: 1 }),
    ).toBeInTheDocument();
    expect(window.location.pathname).toBe("/requests");
    await waitFor(() =>
      expect(screen.getByText("No purchase requests yet")).toBeInTheDocument(),
    );

    vi.unstubAllGlobals();
  });
});
