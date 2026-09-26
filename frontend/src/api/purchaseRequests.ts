export type RequestStatus = "drafting" | "pending_approval" | "approved" | "rejected" | "submitted" | "failed";

export interface PurchaseItem {
  description: string;
  quantity: number;
  unit_price_amount: string;
  currency: string;
  vendor: string | null;
}

export interface PurchaseRequest {
  id: string;
  requester_name: string | null;
  items: PurchaseItem[];
  status: RequestStatus;
  created_at: string;
  updated_at: string;
}

export interface PurchaseRequestPage {
  items: PurchaseRequest[];
  total: number;
  limit: number;
  offset: number;
}

export interface ListPurchaseRequestsQuery {
  status?: RequestStatus;
  limit: number;
  offset: number;
  order: "asc" | "desc";
}

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
  }
}

export interface PurchaseRequestApi {
  list(query: ListPurchaseRequestsQuery): Promise<PurchaseRequestPage>;
}

export class HttpPurchaseRequestApi implements PurchaseRequestApi {
  constructor(private readonly baseUrl = "") {}

  async list(query: ListPurchaseRequestsQuery): Promise<PurchaseRequestPage> {
    const params = new URLSearchParams({
      limit: String(query.limit),
      offset: String(query.offset),
      order: query.order,
    });
    if (query.status) params.set("status", query.status);

    const response = await fetch(`${this.baseUrl}/api/purchase-requests?${params}`);
    if (!response.ok) {
      throw new ApiError(response.status, await readErrorMessage(response));
    }
    return response.json() as Promise<PurchaseRequestPage>;
  }
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    return typeof payload.detail === "string"
      ? payload.detail
      : "Unable to complete the request.";
  } catch {
    return "Unable to complete the request.";
  }
}
