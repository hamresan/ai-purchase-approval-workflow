import { useEffect, useState } from "react";

import type { PurchaseRequestApi, PurchaseRequestDetail as RequestDetailModel } from "@/api/purchaseRequests";
import { RequestStatusBadge } from "@/features/requests/RequestStatusBadge";
import { formatDate, requestAmount, requestTitle } from "@/features/requests/requestPresentation";

interface Props {
  api: PurchaseRequestApi;
  requestId: string;
  onBack: () => void;
}

export function RequestDetail({ api, requestId, onBack }: Props) {
  const [request, setRequest] = useState<RequestDetailModel | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    setState("loading");
    api.get(requestId)
      .then((detail) => {
        if (!active) return;
        setRequest(detail);
        setState("ready");
      })
      .catch(() => active && setState("error"));
    return () => { active = false; };
  }, [api, requestId, reloadKey]);

  if (state === "loading") {
    return <section className="page"><div className="state-panel" aria-label="Loading request details"><div className="spinner" /><h2>Loading request details…</h2></div></section>;
  }
  if (state === "error" || request === null) {
    return <section className="page"><div className="state-panel"><div className="state-icon error">!</div><h2>Unable to load this request</h2><p>Please try again.</p><button className="secondary-button" onClick={() => setReloadKey((value) => value + 1)}>↻ Try Again</button></div></section>;
  }

  const draft = request.draft_order;
  return (
    <section className="page request-detail-page">
      <button className="back-link" onClick={onBack}>← Back to requests</button>
      <div className="detail-heading">
        <div>
          <div className="detail-title"><h1>{requestTitle(request)}</h1><RequestStatusBadge status={request.status} /></div>
          <p>{shortId(request.id)} · Submitted on {formatDate(request.created_at)}</p>
        </div>
      </div>

      <div className="detail-grid">
        <div className="detail-main">
          <article className="detail-card">
            <h2><span className="section-icon">▤</span> Request details</h2>
            <h3>Extracted items</h3>
            <div className="detail-items" role="table" aria-label="Purchase request items">
              <div className="detail-item header" role="row"><span>Item</span><span>Quantity</span><span>Unit Price</span><span>Total</span></div>
              {request.items.map((item, index) => (
                <div className="detail-item" role="row" key={`${item.description}-${index}`}>
                  <span>{item.description}<small>{item.vendor ? `Vendor: ${item.vendor}` : "Vendor not selected"}</small></span>
                  <span>{item.quantity}</span><span>{money(item.unit_price_amount, item.currency)}</span>
                  <span>{money(String(Number(item.unit_price_amount) * item.quantity), item.currency)}</span>
                </div>
              ))}
              <div className="detail-total"><span>Total</span><strong>{requestAmount(request)}</strong></div>
            </div>
          </article>

          <article className="detail-card">
            <h2><span className="section-icon">◷</span> Approval timeline</h2>
            <div className="audit-timeline">
              {request.audit_entries.length === 0
                ? <p className="muted">No timeline events yet.</p>
                : request.audit_entries.map((entry, index) => (
                  <div className="timeline-entry" key={`${entry.event_type}-${entry.occurred_at}-${index}`}>
                    <span className="timeline-dot">✓</span>
                    <div><strong>{timelineTitle(entry.event_type)}</strong><small>{formatDate(entry.occurred_at)}</small></div>
                    <p>{timelineMessage(entry.event_type, entry.message)}</p>
                  </div>
                ))}
            </div>
          </article>
        </div>

        <aside className="detail-side">
          <article className="detail-card">
            <h2><span className="section-icon">ⓘ</span> Request information</h2>
            <dl className="info-list">
              <div><dt>Status</dt><dd><RequestStatusBadge status={request.status} /></dd></div>
              <div><dt>Request ID</dt><dd>{shortId(request.id)}</dd></div>
              <div><dt>Submitted on</dt><dd>{formatDate(request.created_at)}</dd></div>
              <div><dt>Requester</dt><dd>{request.requester_name ?? "Not provided"}</dd></div>
              <div><dt>Budget check</dt><dd>{request.budget_outcome === "passed" ? "Within budget" : "Not checked yet"}</dd></div>
              <div><dt>Vendor</dt><dd>{vendorSummary(request)}</dd></div>
              <div><dt>Draft order</dt><dd>{draft ? money(draft.total_amount, draft.currency) : "Not prepared yet"}</dd></div>
            </dl>
          </article>
          <article className="detail-card documents-card">
            <h2><span className="section-icon">⌕</span> Documents</h2>
            <p>No documents attached</p>
          </article>
        </aside>
      </div>
    </section>
  );
}

function shortId(id: string) {
  return `PR-${id.slice(0, 8).toUpperCase()}`;
}

function money(amount: string, currency: string) {
  const value = Number(amount);
  return Number.isFinite(value)
    ? new Intl.NumberFormat("en-US", { style: "currency", currency }).format(value)
    : "—";
}

function vendorSummary(request: RequestDetailModel) {
  const vendors = [...new Set(request.items.map((item) => item.vendor).filter(Boolean))];
  return vendors.length ? vendors.join(", ") : "Not selected yet";
}

function timelineTitle(eventType: string) {
  const titles: Record<string, string> = {
    request_extracted: "Request submitted",
    trusted_data_validated: "Request validated",
    approval_paused: "Waiting for approval",
    approval_approved: "Request approved",
    approval_rejected: "Request rejected",
    approval_edited: "Request updated",
    order_submitted: "Order submitted",
  };
  return titles[eventType] ?? "Request updated";
}

function timelineMessage(eventType: string, fallback: string) {
  const messages: Record<string, string> = {
    request_extracted: "Request details were prepared for review.",
    trusted_data_validated: "Budget and vendor checks passed and a draft order was prepared.",
    approval_paused: "The request is ready for a human approval decision.",
    approval_approved: "The request was approved by a reviewer.",
    approval_rejected: "The request was rejected by a reviewer.",
    order_submitted: "The approved order was submitted successfully.",
  };
  return messages[eventType] ?? fallback;
}
