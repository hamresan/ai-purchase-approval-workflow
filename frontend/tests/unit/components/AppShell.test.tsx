import { fireEvent, render, screen } from "@testing-library/react";

import { AppShell } from "@/components/AppShell";

describe("AppShell", () => {
  it("navigates through primary actions without implying an authenticated user", () => {
    const onNavigate = vi.fn();
    render(<AppShell route="requests" onNavigate={onNavigate}><div>Content</div></AppShell>);

    fireEvent.click(screen.getByRole("button", { name: /Purchase Requests/ }));
    fireEvent.click(screen.getByRole("button", { name: /New Purchase Request/ }));

    expect(onNavigate).toHaveBeenNthCalledWith(1, "requests");
    expect(onNavigate).toHaveBeenNthCalledWith(2, "new-request");
    expect(screen.getByText("Purchase workspace")).toBeInTheDocument();
    expect(screen.queryByText("John Doe")).not.toBeInTheDocument();
    expect(screen.getByText("Content")).toBeInTheDocument();
  });
});
