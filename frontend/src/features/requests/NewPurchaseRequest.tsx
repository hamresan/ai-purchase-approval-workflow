import { FormEvent, useState } from "react";

import { ApiError } from "@/api/purchaseRequests";
import type { PurchaseRequestSubmissionApi } from "@/api/purchaseRequestSubmission";

interface Props {
  api: PurchaseRequestSubmissionApi;
  onBack: () => void;
}

export function NewPurchaseRequest({ api, onBack }: Props) {
  const [description, setDescription] = useState("");
  const [requesterName, setRequesterName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [state, setState] = useState<"editing" | "submitting" | "success">("editing");
  const [showNextSteps, setShowNextSteps] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const requestText = description.trim();
    if (requestText.length < 10) {
      setError("Please provide more details (at least 10 characters).");
      return;
    }

    setError(null);
    setState("submitting");
    try {
      await api.submit({
        requestText,
        requesterName: requesterName.trim() || undefined,
      });
      setState("success");
    } catch (submissionError) {
      setError(
        submissionError instanceof ApiError
          ? submissionError.message
          : "Unable to submit the purchase request. Please try again.",
      );
      setState("editing");
    }
  };

  if (state === "success") {
    return <section className="page new-request-page"><SuccessState onBack={onBack} onCreateAnother={() => { setDescription(""); setRequesterName(""); setError(null); setState("editing"); }} /></section>;
  }

  return (
    <section className="page new-request-page">
      <button className="back-link" onClick={onBack}>← Back to requests</button>
      <div className="page-heading compact"><div><h1>New Purchase Request</h1><p>Tell us what you need to purchase, and we'll take care of the rest.</p></div></div>
      <div className="new-request-grid">
        <form className="request-form" onSubmit={submit}>
          <FormStep number="1" title="What do you want to purchase?" description="Describe the items or services you need in plain language." active>
            <textarea aria-label="What do you want to purchase?" maxLength={500} disabled={state === "submitting"} value={description} onChange={(event) => { setDescription(event.target.value); setError(null); }} placeholder="For example: I need 5 ergonomic office chairs for our main office, around $300 each, preferably from a trusted supplier." className={error ? "invalid" : ""} />
            <div className="field-footer"><span className="field-error" role={error ? "alert" : undefined}>{error}</span><span>{description.length} / 500</span></div>
          </FormStep>
          <FormStep number="2" title="Your name (optional)" description="Helps identify who made the request.">
            <input aria-label="Your name (optional)" disabled={state === "submitting"} value={requesterName} onChange={(event) => setRequesterName(event.target.value)} placeholder="Enter your name" />
          </FormStep>
          {state === "submitting" && <div className="submission-progress" role="status"><div className="spinner" /><div><strong>Submitting your request…</strong><span>Preparing the workflow and waiting for approval.</span></div></div>}
          <div className="form-actions"><button type="button" className="secondary-button" disabled={state === "submitting"} onClick={onBack}>Cancel</button><button className="primary-button" disabled={state === "submitting"} type="submit">{state === "submitting" ? "Submitting…" : "Submit Request →"}</button></div>
        </form>
        <aside className={showNextSteps ? "next-panel expanded" : "next-panel"}>
          <button type="button" className="next-panel-toggle" aria-expanded={showNextSteps} aria-controls="next-steps" onClick={() => setShowNextSteps((value) => !value)}>
            <span>What happens next?</span><span aria-hidden="true">{showNextSteps ? "−" : "+"}</span>
          </button>
          <h2 className="next-panel-heading">What happens next?</h2>
          <div id="next-steps" className="next-steps">
            <NextItem icon="▤" title="We review your request">We validate your request and find the best options from our trusted suppliers.</NextItem>
            <NextItem icon="🛒" title="A draft order is prepared">We'll create a draft order with item details, pricing, and supplier information.</NextItem>
            <NextItem icon="◉" title="Approval is required">An approver will review the request before it can be placed.</NextItem>
            <NextItem icon="▥" title="You can track progress here">You can check the status of your request on the Purchase Requests page.</NextItem>
          </div>
        </aside>
      </div>
    </section>
  );
}

function SuccessState({ onBack, onCreateAnother }: { onBack: () => void; onCreateAnother: () => void }) {
  return <div className="success-panel"><div className="success-icon">✓</div><h1>Your request has been submitted</h1><p>We're processing your request. You can track its progress on the Purchase Requests page.</p><div className="success-actions"><button className="primary-button" onClick={onBack}>View Requests</button><button className="secondary-button" onClick={onCreateAnother}>Create Another Request</button></div></div>;
}

function FormStep({ number, title, description, active = false, children }: { number: string; title: string; description: string; active?: boolean; children: React.ReactNode }) {
  return <div className="form-step"><span className={active ? "step-number active" : "step-number"}>{number}</span><div className="step-content"><h2>{title}</h2><p>{description}</p>{children}</div></div>;
}
function NextItem({ icon, title, children }: { icon: string; title: string; children: React.ReactNode }) {
  return <div className="next-item"><span className="next-icon">{icon}</span><div><h3>{title}</h3><p>{children}</p></div></div>;
}
