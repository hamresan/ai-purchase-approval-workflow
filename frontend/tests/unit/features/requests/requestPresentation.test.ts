import type { PurchaseRequest } from "@/api/purchaseRequests";
import { requestAmount, requestSummary, requestTitle } from "@/features/requests/requestPresentation";

const request: PurchaseRequest = {
  id: "1", requester_name: "Dana", status: "approved",
  created_at: "2026-09-26T10:00:00Z", updated_at: "2026-09-26T10:00:00Z",
  items: [{ description: "Laptop stand", quantity: 2, unit_price_amount: "35", currency: "USD", vendor: "Acme" }],
};

describe("request presentation", () => {
  it("builds human-readable request values", () => {
    expect(requestTitle(request)).toBe("Laptop stand");
    expect(requestSummary(request)).toBe("2 × Laptop stand");
    expect(requestAmount(request)).toBe("$70");
  });

  it("handles empty and multi-currency requests safely", () => {
    expect(requestTitle({ ...request, items: [] })).toBe("Purchase request");
    expect(requestSummary({ ...request, items: [] })).toBe("No item details");
    expect(requestAmount({ ...request, items: [] })).toBe("—");
    expect(requestAmount({ ...request, items: [...request.items, { ...request.items[0], currency: "EUR" }] })).toBe("Mixed");
  });
});
