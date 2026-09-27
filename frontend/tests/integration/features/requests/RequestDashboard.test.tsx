import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";

import type { PurchaseRequestApi } from "@/api/purchaseRequests";
import { RequestDashboard } from "@/features/requests/RequestDashboard";

const item = {
  id: "1", requester_name: "Dana", status: "pending_approval" as const,
  created_at: "2026-09-26T10:00:00Z", updated_at: "2026-09-26T11:00:00Z",
  items: [{ description: "Laptop stand", quantity: 2, unit_price_amount: "35", currency: "USD", vendor: "Acme" }],
};
const page = { total: 1, limit: 7, offset: 0, items: [item] };

describe("RequestDashboard", () => {
  it("loads, filters, sorts, searches, and paginates purchase requests", async () => {
    const list = vi.fn().mockResolvedValue({ ...page, total: 8 });
    render(<RequestDashboard api={{ list, get: vi.fn() }} onNewRequest={vi.fn()} onOpenRequest={vi.fn()} />);
    expect(screen.getByLabelText("Loading purchase requests")).toBeInTheDocument();
    await waitFor(() => expect(screen.getAllByText("Laptop stand")).toHaveLength(2));

    fireEvent.click(screen.getByRole("button", { name: "Approved" }));
    await waitFor(() => expect(list).toHaveBeenLastCalledWith(expect.objectContaining({ status: "approved" })));

    fireEvent.change(screen.getByLabelText("Sort requests"), { target: { value: "asc" } });
    await waitFor(() => expect(list).toHaveBeenLastCalledWith(expect.objectContaining({ order: "asc", offset: 0 })));

    fireEvent.change(screen.getByPlaceholderText("Search requests..."), { target: { value: "monitor" } });
    expect(screen.getByText("No requests match your search on this page.")).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText("Search requests..."), { target: { value: "" } });
    fireEvent.click(screen.getByRole("button", { name: "Next page" }));
    await waitFor(() => expect(list).toHaveBeenLastCalledWith(expect.objectContaining({ offset: 7 })));
    fireEvent.click(screen.getByRole("button", { name: "Previous page" }));
    await waitFor(() => expect(list).toHaveBeenLastCalledWith(expect.objectContaining({ offset: 0 })));
  });

  it("opens a request from the desktop and mobile presentations", async () => {
    const openRequest = vi.fn();
    render(<RequestDashboard api={{ list: vi.fn().mockResolvedValue(page), get: vi.fn() }} onNewRequest={vi.fn()} onOpenRequest={openRequest} />);
    await waitFor(() => expect(screen.getAllByText("Laptop stand")).toHaveLength(2));
    const row = screen.getAllByText("Laptop stand")[0].closest("tr");
    expect(row).not.toBeNull();
    fireEvent.keyDown(row as HTMLElement, { key: "Enter" });
    expect(openRequest).toHaveBeenCalledWith("1");
    const card = screen.getAllByText("Laptop stand")[1].closest("article");
    expect(card).not.toBeNull();
    fireEvent.click(card as HTMLElement);
    expect(openRequest).toHaveBeenCalledTimes(2);
  });

  it("shows empty and error states with actionable controls", async () => {
    const emptyApi: PurchaseRequestApi = { list: vi.fn().mockResolvedValue({ ...page, total: 0, items: [] }), get: vi.fn() };
    const onNewRequest = vi.fn();
    const { unmount } = render(<RequestDashboard api={emptyApi} onNewRequest={onNewRequest} onOpenRequest={vi.fn()} />);
    const emptyHeading = await screen.findByText("No purchase requests yet");
    const emptyState = emptyHeading.closest(".state-panel");
    expect(emptyState).not.toBeNull();
    fireEvent.click(within(emptyState as HTMLElement).getByRole("button", { name: /New Purchase Request/ }));
    expect(onNewRequest).toHaveBeenCalled();
    unmount();

    const failingApi: PurchaseRequestApi = { list: vi.fn().mockRejectedValue(new Error("offline")), get: vi.fn() };
    render(<RequestDashboard api={failingApi} onNewRequest={vi.fn()} onOpenRequest={vi.fn()} />);
    expect(await screen.findByText("Unable to load purchase requests")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Try Again/ }));
    await waitFor(() => expect(failingApi.list).toHaveBeenCalledTimes(2));
  });
});
