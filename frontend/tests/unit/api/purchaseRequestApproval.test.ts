import { HttpPurchaseRequestApprovalApi } from "@/api/purchaseRequestApproval";

describe("HttpPurchaseRequestApprovalApi", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("posts approval decisions using the backend contract", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ id: "1", status: "approved" }), { status: 200, headers: { "Content-Type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    const api = new HttpPurchaseRequestApprovalApi("http://api.test");

    await api.decide("request 1", { action: "approve", reason: "OK" });

    expect(fetchMock).toHaveBeenCalledWith("http://api.test/api/purchase-requests/request%201/approval", expect.objectContaining({
      method: "POST",
      body: JSON.stringify({ action: "approve", reason: "OK", items: null }),
    }));
  });

  it("does not expose structured server errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: [{ secret: "internal" }] }), { status: 422, headers: { "Content-Type": "application/json" } })));
    const api = new HttpPurchaseRequestApprovalApi();

    await expect(api.decide("1", { action: "reject", reason: "No" })).rejects.toThrow("Unable to update this request.");
  });
});
