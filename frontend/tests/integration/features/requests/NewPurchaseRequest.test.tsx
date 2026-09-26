import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { ApiError } from "@/api/purchaseRequests";
import type { PurchaseRequestSubmissionApi } from "@/api/purchaseRequestSubmission";
import { NewPurchaseRequest } from "@/features/requests/NewPurchaseRequest";

function renderForm(api: PurchaseRequestSubmissionApi = { submit: vi.fn() }) {
  return render(<NewPurchaseRequest api={api} onBack={vi.fn()} />);
}

describe("NewPurchaseRequest", () => {
  it("validates plain-language request text", () => {
    renderForm();
    fireEvent.change(screen.getByLabelText("What do you want to purchase?"), { target: { value: "laptop" } });
    fireEvent.click(screen.getByRole("button", { name: /Submit Request/ }));
    expect(screen.getByRole("alert")).toHaveTextContent("Please provide more details");
  });

  it("submits trimmed form data and renders the approved success state", async () => {
    const submit = vi.fn().mockResolvedValue({ requestId: "request-1", status: "pending_approval" });
    renderForm({ submit });
    fireEvent.change(screen.getByLabelText("What do you want to purchase?"), { target: { value: "  I need two laptop stands  " } });
    fireEvent.change(screen.getByLabelText("Your name (optional)"), { target: { value: "  Dana  " } });
    fireEvent.click(screen.getByRole("button", { name: /Submit Request/ }));

    await waitFor(() => expect(submit).toHaveBeenCalledWith({ requestText: "I need two laptop stands", requesterName: "Dana" }));
    expect(await screen.findByRole("heading", { name: "Your request has been submitted" })).toBeInTheDocument();
  });

  it("shows safe server validation errors", async () => {
    const submit = vi.fn().mockRejectedValue(new ApiError(422, "Please check the request details and try again."));
    renderForm({ submit });
    fireEvent.change(screen.getByLabelText("What do you want to purchase?"), { target: { value: "I need two laptop stands" } });
    fireEvent.click(screen.getByRole("button", { name: /Submit Request/ }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Please check the request details");
  });
});
