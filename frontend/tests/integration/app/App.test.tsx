import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";

import { App } from "@/app/App";

const sessionKey = "purchase-approval.auth-session";
const initialSession = {
  userId: "user-1",
  accessToken: "token",
  refreshToken: "refresh",
};

describe("App", () => {
  beforeEach(() => {
    window.localStorage.setItem(sessionKey, JSON.stringify(initialSession));
  });

  afterEach(() => {
    window.localStorage.clear();
    vi.unstubAllGlobals();
  });

  it("renders the purchase request application shell and navigates back", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ items: [], total: 0, limit: 7, offset: 0 }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
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
  });

  it("synchronizes the rendered route with browser history navigation", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ items: [], total: 0, limit: 7, offset: 0 }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    window.history.replaceState({}, "", "/requests/new");
    render(<App />);

    window.history.replaceState({}, "", "/requests");
    act(() => window.dispatchEvent(new PopStateEvent("popstate")));

    expect(
      screen.getByRole("heading", { name: "Purchase Requests", level: 1 }),
    ).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByText("No purchase requests yet")).toBeInTheDocument(),
    );
  });

  it("revokes the refresh session and returns to authentication on sign out", async () => {
    const fetchMock = vi.fn().mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/identity/sessions/revoke")) {
        return Promise.resolve(new Response(null, { status: 204 }));
      }
      return Promise.resolve(
        new Response(JSON.stringify({ items: [], total: 0, limit: 7, offset: 0 }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );
    });
    vi.stubGlobal("fetch", fetchMock);
    window.history.replaceState({}, "", "/requests");

    render(<App />);
    await screen.findByRole("heading", { name: "Purchase Requests", level: 1 });
    fireEvent.click(screen.getByRole("button", { name: /Sign out/i }));

    await screen.findByRole("heading", { name: "Welcome back", level: 1 });
    expect(window.localStorage.getItem(sessionKey)).toBeNull();
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/identity/sessions/revoke",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ refresh_token: "refresh" }),
        }),
      ),
    );
  });
});
