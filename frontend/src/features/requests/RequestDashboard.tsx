import { useEffect, useMemo, useState } from "react";

import type { PurchaseRequest, PurchaseRequestApi, RequestStatus } from "@/api/purchaseRequests";
import { RequestStatusBadge } from "@/features/requests/RequestStatusBadge";
import { formatDate, requestAmount, requestSummary, requestTitle } from "@/features/requests/requestPresentation";

const pageSize = 7;
const filters: Array<{ label: string; value?: RequestStatus }> = [
  { label: "All" },
  { label: "Pending Approval", value: "pending_approval" },
  { label: "Approved", value: "approved" },
  { label: "Rejected", value: "rejected" },
  { label: "Submitted", value: "submitted" },
  { label: "Failed", value: "failed" },
];

interface Props {
  api: PurchaseRequestApi;
  onNewRequest: () => void;
}

export function RequestDashboard({ api, onNewRequest }: Props) {
  const [status, setStatus] = useState<RequestStatus | undefined>();
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const [offset, setOffset] = useState(0);
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<PurchaseRequest[]>([]);
  const [total, setTotal] = useState(0);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    setState("loading");
    api.list({ status, limit: pageSize, offset, order })
      .then((page) => {
        if (!active) return;
        setItems(page.items);
        setTotal(page.total);
        setState("ready");
      })
      .catch(() => active && setState("error"));
    return () => { active = false; };
  }, [api, status, order, offset, reloadKey]);

  const visibleItems = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return items;
    return items.filter((request) =>
      [requestTitle(request), requestSummary(request), request.requester_name ?? ""]
        .some((value) => value.toLowerCase().includes(normalized)),
    );
  }, [items, query]);

  const selectFilter = (value?: RequestStatus) => {
    setStatus(value);
    setOffset(0);
  };

  return (
    <section className="page">
      <div className="page-heading">
        <div><h1>Purchase Requests</h1><p>Create and track your purchase requests</p></div>
        <button className="primary-button" onClick={onNewRequest}>＋ New Purchase Request</button>
      </div>

      <div className="filter-tabs" aria-label="Request status filters">
        {filters.map((filter) => (
          <button key={filter.label} className={status === filter.value ? "filter-tab active" : "filter-tab"} onClick={() => selectFilter(filter.value)}>
            {filter.label}
          </button>
        ))}
      </div>

      <div className="dashboard-tools">
        <label className="search-box"><span>⌕</span><span className="sr-only">Search requests</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search requests..." /></label>
        <select aria-label="Sort requests" value={order} onChange={(event) => { setOrder(event.target.value as "asc" | "desc"); setOffset(0); }}>
          <option value="desc">Newest first</option>
          <option value="asc">Oldest first</option>
        </select>
      </div>

      {state === "loading" && <LoadingState />}
      {state === "error" && <ErrorState onRetry={() => setReloadKey((value) => value + 1)} />}
      {state === "ready" && total === 0 && <EmptyState onNewRequest={onNewRequest} />}
      {state === "ready" && total > 0 && (
        <>
          <div className="request-table-wrap">
            <table className="request-table">
              <thead><tr><th>Request</th><th>Requester</th><th>Amount (Est.)</th><th>Status</th><th>Submitted</th><th>Last Updated</th><th>Actions</th></tr></thead>
              <tbody>{visibleItems.map((request) => <RequestRow key={request.id} request={request} />)}</tbody>
            </table>
          </div>
          <div className="request-cards">{visibleItems.map((request) => <RequestCard key={request.id} request={request} />)}</div>
          {visibleItems.length === 0 && <div className="inline-empty">No requests match your search on this page.</div>}
          <div className="pagination">
            <span>Showing {offset + 1}–{Math.min(offset + pageSize, total)} of {total} requests</span>
            <div>
              <button aria-label="Previous page" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - pageSize))}>‹</button>
              <button aria-label="Next page" disabled={offset + pageSize >= total} onClick={() => setOffset(offset + pageSize)}>›</button>
            </div>
          </div>
        </>
      )}
    </section>
  );
}

function RequestRow({ request }: { request: PurchaseRequest }) {
  return <tr>
    <td><strong>{requestTitle(request)}</strong><small>{requestSummary(request)}</small></td>
    <td>{request.requester_name ?? "—"}</td><td><strong>{requestAmount(request)}</strong></td>
    <td><RequestStatusBadge status={request.status} /></td><td>{formatDate(request.created_at)}</td><td>{formatDate(request.updated_at)}</td>
    <td><button className="secondary-button">View</button></td>
  </tr>;
}

function RequestCard({ request }: { request: PurchaseRequest }) {
  return <article className="request-card"><div><strong>{requestTitle(request)}</strong><small>{requestSummary(request)}</small></div><RequestStatusBadge status={request.status} /><div className="card-meta"><strong>{requestAmount(request)}</strong><span>{formatDate(request.created_at)}</span></div></article>;
}

function LoadingState() {
  return <div className="state-panel" aria-label="Loading purchase requests"><div className="spinner" /><h2>Loading purchase requests…</h2></div>;
}
function EmptyState({ onNewRequest }: { onNewRequest: () => void }) {
  return <div className="state-panel"><div className="state-icon">▤</div><h2>No purchase requests yet</h2><p>Create your first purchase request to get started.</p><button className="primary-button" onClick={onNewRequest}>＋ New Purchase Request</button></div>;
}
function ErrorState({ onRetry }: { onRetry: () => void }) {
  return <div className="state-panel"><div className="state-icon error">!</div><h2>Unable to load purchase requests</h2><p>Something went wrong. Please try again.</p><button className="secondary-button" onClick={onRetry}>↻ Try Again</button></div>;
}
