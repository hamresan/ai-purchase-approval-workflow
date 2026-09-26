import { ApiError, HttpPurchaseRequestApi } from "@/api/purchaseRequests";

describe("HttpPurchaseRequestApi", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("lists requests with validated query parameters", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ items: [], total: 0, limit: 7, offset: 0 }), { status: 200, headers: { "Content-Type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    const api = new HttpPurchaseRequestApi("http://api.test");

    await expect(api.list({ status: "approved", limit: 7, offset: 0, order: "desc" })).resolves.toEqual({ items: [], total: 0, limit: 7, offset: 0 });
    expect(fetchMock).toHaveBeenCalledWith("http://api.test/api/purchase-requests?limit=7&offset=0&order=desc&status=approved");
  });

  it("omits the optional status filter", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ items: [], total: 0, limit: 7, offset: 7 }), { status: 200, headers: { "Content-Type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    const api = new HttpPurchaseRequestApi();

    await api.list({ limit: 7, offset: 7, order: "asc" });
    expect(fetchMock).toHaveBeenCalledWith("/api/purchase-requests?limit=7&offset=7&order=asc");
  });

  it("maps API error details to a typed error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Service unavailable." }), { status: 503, headers: { "Content-Type": "application/json" } })));
    const api = new HttpPurchaseRequestApi();

    await expect(api.list({ limit: 7, offset: 0, order: "desc" })).rejects.toEqual(new ApiError(503, "Service unavailable."));
  });

  it("uses a safe message for malformed error bodies", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("not-json", { status: 500 })));
    const api = new HttpPurchaseRequestApi();

    await expect(api.list({ limit: 7, offset: 0, order: "desc" })).rejects.toMatchObject({ status: 500, message: "Unable to complete the request." });
  });
});
