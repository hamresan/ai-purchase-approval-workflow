import { ApiError } from "@/api/purchaseRequests";
import { HttpPurchaseRequestSubmissionApi } from "@/api/purchaseRequestSubmission";

describe("HttpPurchaseRequestSubmissionApi", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("submits the public free-text API contract", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ request_id: "request-1", status: "pending_approval" }), { status: 201, headers: { "Content-Type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);

    const result = await new HttpPurchaseRequestSubmissionApi("http://api.test").submit({ requestText: "Two laptop stands", requesterName: "Dana" });

    expect(result).toEqual({ requestId: "request-1", status: "pending_approval" });
    expect(fetchMock).toHaveBeenCalledWith("http://api.test/api/purchase-requests", expect.objectContaining({
      method: "POST",
      body: JSON.stringify({ request_text: "Two laptop stands", requester_name: "Dana" }),
    }));
  });

  it("accepts the transitional id response shape", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ id: "request-2", status: "drafting" }), { status: 201, headers: { "Content-Type": "application/json" } })));
    await expect(new HttpPurchaseRequestSubmissionApi().submit({ requestText: "Two monitors" })).resolves.toEqual({ requestId: "request-2", status: "drafting" });
  });

  it("maps structured validation failures to a safe message", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: [{ msg: "invalid" }] }), { status: 422, headers: { "Content-Type": "application/json" } })));
    await expect(new HttpPurchaseRequestSubmissionApi().submit({ requestText: "Two monitors" })).rejects.toEqual(new ApiError(422, "Please check the request details and try again."));
  });

  it("rejects invalid successful responses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ status: "pending_approval" }), { status: 201, headers: { "Content-Type": "application/json" } })));
    await expect(new HttpPurchaseRequestSubmissionApi().submit({ requestText: "Two monitors" })).rejects.toMatchObject({ status: 502 });
  });
});
