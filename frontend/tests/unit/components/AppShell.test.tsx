import { fireEvent, render, screen } from "@testing-library/react";

import { AppShell } from "@/components/AppShell";

describe("AppShell", () => {
  it("navigates through primary actions without implying an authenticated user", () => {
    const onNavigate = vi.fn();
    render(
      <AppShell
        route="requests"
        isAdmin={false}
        onNavigate={onNavigate}
        onSignOut={vi.fn()}
      >
        <div>Content</div>
      </AppShell>,
    );

    fireEvent.click(screen.getByRole("button", { name: /Purchase Requests/ }));
    fireEvent.click(screen.getByRole("button", { name: /New Purchase Request/ }));

    expect(onNavigate).toHaveBeenNthCalledWith(1, "requests");
    expect(onNavigate).toHaveBeenNthCalledWith(2, "new-request");
    expect(screen.queryByRole("button", { name: /Admin Management/ })).not.toBeInTheDocument();
    expect(screen.getByText("Purchase workspace")).toBeInTheDocument();
    expect(screen.queryByText("John Doe")).not.toBeInTheDocument();
    expect(screen.getByText("Content")).toBeInTheDocument();
  });

  it("shows admin navigation to administrators", () => {
    const onNavigate = vi.fn();
    render(
      <AppShell
        route="requests"
        isAdmin
        onNavigate={onNavigate}
        onSignOut={vi.fn()}
      >
        <div>Content</div>
      </AppShell>,
    );

    fireEvent.click(screen.getByRole("button", { name: /Admin Management/ }));

    expect(onNavigate).toHaveBeenCalledWith("admin");
  });
});
