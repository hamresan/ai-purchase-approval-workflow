import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";

import { App } from "@/app/App";

describe("App", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("renders the purchase request application shell and navigates back", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ items: [], total: 0, limit: 7, offset: 0 }), { status: 200, headers: { "Content-Type": "application/json" } })));
    window.history.replaceState({}, "", "/requests/new");

    render(<App />);
    expect(screen.getByRole("heading", { name: "New Purchase Request", level: 1 })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Back to requests/ }));
    expect(screen.getByRole("heading", { name: "Purchase Requests", level: 1 })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/requests");
    await waitFor(() => expect(screen.getByText("No purchase requests yet")).toBeInTheDocument());
  });

  it("synchronizes the rendered route with browser history navigation", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ items: [], total: 0, limit: 7, offset: 0 }), { status: 200, headers: { "Content-Type": "application/json" } })));
    window.history.replaceState({}, "", "/requests/new");
    render(<App />);

    window.history.replaceState({}, "", "/requests");
    act(() => window.dispatchEvent(new PopStateEvent("popstate")));

    expect(screen.getByRole("heading", { name: "Purchase Requests", level: 1 })).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("No purchase requests yet")).toBeInTheDocument());
  });
});
