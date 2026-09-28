import type { AuthorizedHttpClient } from "@/api/httpClient";
import type { PurchaseItem, PurchaseRequest } from "@/api/purchaseRequests";
export type ApprovalAction = "approve" | "reject" | "edit";
export interface ApprovalCommand { action: ApprovalAction; reason?: string; items?: Array<Pick<PurchaseItem, "description" | "quantity">>; }
export interface PurchaseRequestApprovalApi { decide(requestId: string, command: ApprovalCommand): Promise<PurchaseRequest>; }
export class HttpPurchaseRequestApprovalApi implements PurchaseRequestApprovalApi {
  constructor(private readonly baseUrl = "", private readonly http: Pick<AuthorizedHttpClient, "fetch"> = { fetch: (input, init) => fetch(input, init) }) {}
  async decide(requestId: string, command: ApprovalCommand): Promise<PurchaseRequest> {
    const response = await this.http.fetch(`${this.baseUrl}/api/purchase-requests/${encodeURIComponent(requestId)}/approval`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: command.action, reason: command.reason || null, items: command.items ?? null }) });
    if (!response.ok) throw new Error(await safeMessage(response)); return response.json() as Promise<PurchaseRequest>;
  }
}
async function safeMessage(response: Response) { try { const payload = (await response.json()) as { detail?: unknown }; return typeof payload.detail === "string" ? payload.detail : "Unable to update this request."; } catch { return "Unable to update this request."; } }
