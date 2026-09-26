import { FormEvent, useState } from "react";

interface Props {
  onBack: () => void;
}

export function NewPurchaseRequest({ onBack }: Props) {
  const [description, setDescription] = useState("");
  const [requesterName, setRequesterName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const value = description.trim();
    if (value.length < 10) {
      setError("Please provide more details (at least 10 characters).");
      return;
    }
    setError("Plain-language workflow submission will be connected when the workflow provider boundary is available.");
  };

  return (
    <section className="page new-request-page">
      <button className="back-link" onClick={onBack}>← Back to requests</button>
      <div className="page-heading compact"><div><h1>New Purchase Request</h1><p>Tell us what you need to purchase, and we'll take care of the rest.</p></div></div>
      <div className="new-request-grid">
        <form className="request-form" onSubmit={submit}>
          <FormStep number="1" title="What do you want to purchase?" description="Describe the items or services you need in plain language." active>
            <textarea aria-label="What do you want to purchase?" maxLength={500} value={description} onChange={(event) => { setDescription(event.target.value); setError(null); }} placeholder="For example: I need 5 ergonomic office chairs for our main office, around $300 each, preferably from a trusted supplier." className={error ? "invalid" : ""} />
            <div className="field-footer"><span className="field-error">{error}</span><span>{description.length} / 500</span></div>
          </FormStep>
          <FormStep number="2" title="Your name (optional)" description="Helps identify who made the request.">
            <input aria-label="Your name (optional)" value={requesterName} onChange={(event) => setRequesterName(event.target.value)} placeholder="Enter your name" />
          </FormStep>
          <div className="form-actions"><button type="button" className="secondary-button" onClick={onBack}>Cancel</button><button className="primary-button" type="submit">Submit Request →</button></div>
        </form>
        <aside className="next-panel"><h2>What happens next?</h2><NextItem icon="▤" title="We review your request">We validate your request and find the best options from our trusted suppliers.</NextItem><NextItem icon="🛒" title="A draft order is prepared">We'll create a draft order with item details, pricing, and supplier information.</NextItem><NextItem icon="◉" title="Approval is required">An approver will review the request before it can be placed.</NextItem><NextItem icon="▥" title="You can track progress here">You can check the status of your request on the Purchase Requests page.</NextItem></aside>
      </div>
    </section>
  );
}

function FormStep({ number, title, description, active = false, children }: { number: string; title: string; description: string; active?: boolean; children: React.ReactNode }) {
  return <div className="form-step"><span className={active ? "step-number active" : "step-number"}>{number}</span><div className="step-content"><h2>{title}</h2><p>{description}</p>{children}</div></div>;
}
function NextItem({ icon, title, children }: { icon: string; title: string; children: React.ReactNode }) {
  return <div className="next-item"><span className="next-icon">{icon}</span><div><h3>{title}</h3><p>{children}</p></div></div>;
}
