import type { RequestStatus } from "@/api/purchaseRequests";
import { statusLabels } from "@/features/requests/requestPresentation";

export function RequestStatusBadge({ status }: { status: RequestStatus }) {
  return <span className={`status-badge status-${status}`}>{statusLabels[status]}</span>;
}
