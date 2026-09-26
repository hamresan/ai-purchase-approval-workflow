import { ApiError } from "@/api/purchaseRequests";

export interface SubmitPurchaseRequestCommand {
  requestText: string;
  requesterName?: string;
}

export interface SubmitPurchaseRequestResult {
  requestId: string;
  status: string;
}

export interface PurchaseRequestSubmissionApi {
  submit(command: SubmitPurchaseRequestCommand): Promise<SubmitPurchaseRequestResult>;
}

export class HttpPurchaseRequestSubmissionApi implements PurchaseRequestSubmissionApi {
  constructor(private readonly baseUrl = "") {}

  async submit(command: SubmitPurchaseRequestCommand): Promise<SubmitPurchaseRequestResult> {
    const response = await fetch(`${this.baseUrl}/api/purchase-requests`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        request_text: command.requestText,
        requester_name: command.requesterName || null,
      }),
    });

    if (!response.ok) {
      throw new ApiError(response.status, await readSubmissionError(response));
    }

    const payload = (await response.json()) as Record<string, unknown>;
    const requestId = payload.request_id ?? payload.id;
    if (typeof requestId !== "string" || typeof payload.status !== "string") {
      throw new ApiError(502, "The server returned an invalid purchase request response.");
    }
    return { requestId, status: payload.status };
  }
}

async function readSubmissionError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") return payload.detail;
    if (Array.isArray(payload.detail)) return "Please check the request details and try again.";
  } catch {
    return "Unable to submit the purchase request.";
  }
  return "Unable to submit the purchase request.";
}
