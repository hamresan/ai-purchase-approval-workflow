import { useState } from "react";

import type { ApprovalAction, PurchaseRequestApprovalApi } from "@/api/purchaseRequestApproval";
import type { PurchaseRequestDetail } from "@/api/purchaseRequests";

interface Props {
  action: ApprovalAction;
  request: PurchaseRequestDetail;
  api: PurchaseRequestApprovalApi;
  onClose: () => void;
  onCompleted: () => void;
}

export function ApprovalDialog({ action, request, api, onClose, onCompleted }: Props) {
  const [reason, setReason] = useState("");
  const [reviewer, setReviewer] = useState("");
  const [items, setItems] = useState(request.items.map((item) => ({ description: item.description, quantity: item.quantity })));
  const [state, setState] = useState<"editing" | "saving">("editing");
  const [error, setError] = useState("");

  const submit = async () => {
    if (!reviewer.trim()) {
      setError("Please enter your name.");
      return;
    }
    if (action === "reject" && !reason.trim()) {
      setError("Please provide a reason for rejection.");
      return;
    }
    if (action === "edit" && items.some((item) => !item.description.trim() || item.quantity < 1)) {
      setError("Each item needs a description and quantity of at least 1.");
      return;
    }
    setState("saving");
    setError("");
    try {
      await api.decide(request.id, {
        action,
        decidedBy: reviewer.trim(),
        reason: action === "edit" ? undefined : reason.trim() || undefined,
        items: action === "edit" ? items.map((item) => ({ ...item, description: item.description.trim() })) : undefined,
      });
      onCompleted();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to update this request.");
      setState("editing");
    }
  };

  const title = action === "approve" ? "Approve request" : action === "reject" ? "Reject request" : "Edit request";
  return (
    <div className="modal-backdrop" role="presentation">
      <section className="approval-dialog" role="dialog" aria-modal="true" aria-labelledby="approval-dialog-title">
        <div className="dialog-heading">
          <span className={action === "reject" ? "dialog-icon danger" : "dialog-icon"}>{action === "approve" ? "✓" : action === "reject" ? "×" : "✎"}</span>
          <div><h2 id="approval-dialog-title">{title}</h2><p>{action === "edit" ? "Update the request items before approval." : `Are you sure you want to ${action} this purchase request?`}</p></div>
          <button className="dialog-close" aria-label="Close dialog" onClick={onClose}>×</button>
        </div>

        <label className="dialog-field">Reviewer name *
          <input aria-label="Reviewer name" value={reviewer} onChange={(event) => setReviewer(event.target.value)} placeholder="Enter your name" />
        </label>
        {action === "edit" ? (
          <div className="edit-items">
            {items.map((item, index) => (
              <div className="edit-item" key={index}>
                <label>Item description<input aria-label={`Item ${index + 1} description`} value={item.description} onChange={(event) => setItems((current) => current.map((value, itemIndex) => itemIndex === index ? { ...value, description: event.target.value } : value))} /></label>
                <label>Quantity<input aria-label={`Item ${index + 1} quantity`} type="number" min="1" value={item.quantity} onChange={(event) => setItems((current) => current.map((value, itemIndex) => itemIndex === index ? { ...value, quantity: Number(event.target.value) } : value))} /></label>
              </div>
            ))}
            <p className="dialog-note">Vendor, pricing, draft order, and budget checks are revalidated by the trusted backend after you save.</p>
          </div>
        ) : (
          <label className="dialog-field">{action === "reject" ? "Reason *" : "Comment (optional)"}
            <textarea value={reason} onChange={(event) => setReason(event.target.value)} placeholder={action === "reject" ? "Please provide a reason for rejection..." : "Add a comment..."} />
          </label>
        )}

        {error && <p className="dialog-error" role="alert">{error}</p>}
        <div className="dialog-actions">
          <button className="secondary-button" onClick={onClose} disabled={state === "saving"}>Cancel</button>
          <button className={action === "reject" ? "danger-button" : "primary-button"} onClick={submit} disabled={state === "saving"}>
            {state === "saving" ? "Saving…" : action === "edit" ? "Save changes" : action === "approve" ? "Approve" : "Reject"}
          </button>
        </div>
      </section>
    </div>
  );
}
