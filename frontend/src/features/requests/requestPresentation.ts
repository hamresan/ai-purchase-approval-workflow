import type { PurchaseRequest, RequestStatus } from "@/api/purchaseRequests";

export const statusLabels: Record<RequestStatus, string> = {
  drafting: "Drafting",
  pending_approval: "Pending Approval",
  approved: "Approved",
  rejected: "Rejected",
  submitted: "Submitted",
  failed: "Failed",
};

export function requestTitle(request: PurchaseRequest): string {
  if (request.items.length === 0) return "Purchase request";
  const first = request.items[0];
  return request.items.length === 1
    ? first.description
    : `${first.description} + ${request.items.length - 1} more`;
}

export function requestSummary(request: PurchaseRequest): string {
  if (request.items.length === 0) return "No item details";
  return request.items
    .slice(0, 2)
    .map((item) => `${item.quantity} × ${item.description}`)
    .join(", ");
}

export function requestAmount(request: PurchaseRequest): string {
  if (request.items.length === 0) return "—";
  const currencies = new Set(request.items.map((item) => item.currency));
  if (currencies.size !== 1) return "Mixed";
  const total = request.items.reduce(
    (sum, item) => sum + Number(item.unit_price_amount) * item.quantity,
    0,
  );
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: request.items[0].currency,
    maximumFractionDigits: 0,
  }).format(total);
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}
