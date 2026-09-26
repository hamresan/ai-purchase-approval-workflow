import { fireEvent, render, screen } from "@testing-library/react";

import { AppShell } from "@/components/AppShell";

describe("AppShell", () => {
  it("navigates through the primary actions", () => {
    const onNavigate = vi.fn();
    render(<AppShell route="requests" onNavigate={onNavigate}><div>Content</div></AppShell>);

    fireEvent.click(screen.getByRole("button", { name: /Purchase Requests/ }));
    fireEvent.click(screen.getByRole("button", { name: /New Purchase Request/ }));

    expect(onNavigate).toHaveBeenNthCalledWith(1, "requests");
    expect(onNavigate).toHaveBeenNthCalledWith(2, "new-request");
    expect(screen.getByText("Content")).toBeInTheDocument();
  });
});
