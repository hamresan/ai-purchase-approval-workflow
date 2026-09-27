import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import type { PurchaseRequestApi, PurchaseRequestDetail } from "@/api/purchaseRequests";
import { RequestDetail } from "@/features/requests/RequestDetail";

const detail: PurchaseRequestDetail = {
  id: "12345678-1234-1234-1234-123456789012",
  requester_name: "Dana",
  status: "pending_approval",
  created_at: "2026-09-27T08:00:00Z",
  updated_at: "2026-09-27T08:10:00Z",
  items: [{ description: "Laptop stand", quantity: 2, unit_price_amount: "35", currency: "USD", vendor: "Acme" }],
  budget_outcome: "passed",
  draft_order: { id: "draft-1", items: [], total_amount: "70", currency: "USD", created_at: "2026-09-27T08:05:00Z" },
  approval_decision: null,
  audit_entries: [
    { event_type: "trusted_data_validated", message: "internal message", occurred_at: "2026-09-27T08:05:00Z" },
    { event_type: "approval_paused", message: "internal pause wording", occurred_at: "2026-09-27T08:06:00Z" },
  ],
};

const api: PurchaseRequestApi = {
  list: vi.fn(),
  get: vi.fn().mockResolvedValue(detail),
};

describe("RequestDetail", () => {
  it("renders trusted request detail with non-technical timeline language", async () => {
    render(<RequestDetail api={api} approvalApi={{ decide: vi.fn() }} requestId={detail.id} onBack={vi.fn()} />);
    expect(screen.getByLabelText("Loading request details")).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Laptop stand" })).toBeInTheDocument();
    expect(screen.getByText("Within budget")).toBeInTheDocument();
    expect(screen.getAllByText("Acme").length).toBeGreaterThan(0);
    expect(screen.getByText("Waiting for approval")).toBeInTheDocument();
    expect(screen.queryByText(/workflow paused/i)).not.toBeInTheDocument();
  });

  it("retries after a safe loading error", async () => {
    const get = vi.fn().mockRejectedValueOnce(new Error("database secret")).mockResolvedValueOnce(detail);
    render(<RequestDetail api={{ list: vi.fn(), get }} approvalApi={{ decide: vi.fn() }} requestId={detail.id} onBack={vi.fn()} />);
    expect(await screen.findByText("Unable to load this request")).toBeInTheDocument();
    expect(screen.queryByText("database secret")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Try Again/ }));
    await waitFor(() => expect(get).toHaveBeenCalledTimes(2));
    expect(await screen.findByRole("heading", { name: "Laptop stand" })).toBeInTheDocument();
  });
});
