import type { AuthorizedHttpClient } from "@/api/httpClient";
export type RequestStatus = "drafting" | "pending_approval" | "approved" | "rejected" | "submitted" | "failed";
export interface PurchaseItem { description: string; quantity: number; unit_price_amount: string; currency: string; vendor: string | null; }
export interface PurchaseRequest { id: string; requester_name: string | null; items: PurchaseItem[]; status: RequestStatus; created_at: string; updated_at: string; }
export interface DraftOrder { id: string; items: PurchaseItem[]; total_amount: string; currency: string; created_at: string; }
export interface ApprovalDecision { outcome: "approved" | "rejected"; decided_by: string; reason: string | null; decided_at: string; }
export interface AuditEntry { event_type: string; message: string; occurred_at: string; }
export interface PurchaseRequestDetail extends PurchaseRequest { budget_outcome: "passed" | "not_checked"; draft_order: DraftOrder | null; approval_decision: ApprovalDecision | null; audit_entries: AuditEntry[]; }
export interface PurchaseRequestPage { items: PurchaseRequest[]; total: number; limit: number; offset: number; }
export interface ListPurchaseRequestsQuery { status?: RequestStatus; limit: number; offset: number; order: "asc" | "desc"; }
export class ApiError extends Error { constructor(public readonly status: number, message: string) { super(message); } }
export interface PurchaseRequestApi { list(query: ListPurchaseRequestsQuery): Promise<PurchaseRequestPage>; get(requestId: string): Promise<PurchaseRequestDetail>; }
export class HttpPurchaseRequestApi implements PurchaseRequestApi {
  constructor(private readonly baseUrl = "", private readonly http: Pick<AuthorizedHttpClient, "fetch"> = { fetch: (input, init) => fetch(input, init) }) {}
  async list(query: ListPurchaseRequestsQuery): Promise<PurchaseRequestPage> {
    const params = new URLSearchParams({ limit: String(query.limit), offset: String(query.offset), order: query.order });
    if (query.status) params.set("status", query.status);
    const response = await this.http.fetch(`${this.baseUrl}/api/purchase-requests?${params}`);
    if (!response.ok) throw new ApiError(response.status, await readErrorMessage(response));
    return response.json() as Promise<PurchaseRequestPage>;
  }
  async get(requestId: string): Promise<PurchaseRequestDetail> {
    const response = await this.http.fetch(`${this.baseUrl}/api/purchase-requests/${encodeURIComponent(requestId)}`);
    if (!response.ok) throw new ApiError(response.status, await readErrorMessage(response));
    return response.json() as Promise<PurchaseRequestDetail>;
  }
}
async function readErrorMessage(response: Response): Promise<string> { try { const payload = (await response.json()) as { detail?: unknown }; return typeof payload.detail === "string" ? payload.detail : "Unable to complete the request."; } catch { return "Unable to complete the request."; } }
