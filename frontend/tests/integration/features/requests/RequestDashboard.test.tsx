import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import type { PurchaseRequestApi } from "@/api/purchaseRequests";
import { RequestDashboard } from "@/features/requests/RequestDashboard";

const page = {
  total: 1, limit: 7, offset: 0,
  items: [{
    id: "1", requester_name: "Dana", status: "pending_approval" as const,
    created_at: "2026-09-26T10:00:00Z", updated_at: "2026-09-26T11:00:00Z",
    items: [{ description: "Laptop stand", quantity: 2, unit_price_amount: "35", currency: "USD", vendor: "Acme" }],
  }],
};

describe("RequestDashboard", () => {
  it("loads and filters purchase requests", async () => {
    const list = vi.fn().mockResolvedValue(page);
    render(<RequestDashboard api={{ list }} onNewRequest={vi.fn()} />);
    expect(screen.getByLabelText("Loading purchase requests")).toBeInTheDocument();
    expect(await screen.findByText("Laptop stand")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Approved" }));
    await waitFor(() => expect(list).toHaveBeenLastCalledWith(expect.objectContaining({ status: "approved" })));
  });

  it("shows empty and error states with actionable controls", async () => {
    const emptyApi: PurchaseRequestApi = { list: vi.fn().mockResolvedValue({ ...page, total: 0, items: [] }) };
    const onNewRequest = vi.fn();
    const { unmount } = render(<RequestDashboard api={emptyApi} onNewRequest={onNewRequest} />);
    expect(await screen.findByText("No purchase requests yet")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /New Purchase Request/ }));
    expect(onNewRequest).toHaveBeenCalled();
    unmount();

    const failingApi: PurchaseRequestApi = { list: vi.fn().mockRejectedValue(new Error("offline")) };
    render(<RequestDashboard api={failingApi} onNewRequest={vi.fn()} />);
    expect(await screen.findByText("Unable to load purchase requests")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Try Again/ }));
    await waitFor(() => expect(failingApi.list).toHaveBeenCalledTimes(2));
  });
});
