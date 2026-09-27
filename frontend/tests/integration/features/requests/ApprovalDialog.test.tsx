import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import type { PurchaseRequestApprovalApi } from "@/api/purchaseRequestApproval";
import type { PurchaseRequestDetail } from "@/api/purchaseRequests";
import { ApprovalDialog } from "@/features/requests/ApprovalDialog";

const request: PurchaseRequestDetail = {
  id: "request-1", requester_name: "Dana", status: "pending_approval",
  created_at: "2026-09-27T08:00:00Z", updated_at: "2026-09-27T08:00:00Z",
  items: [{ description: "Laptop stand", quantity: 2, unit_price_amount: "35", currency: "USD", vendor: "Acme" }],
  budget_outcome: "passed", draft_order: null, approval_decision: null, audit_entries: [],
};

describe("ApprovalDialog", () => {
  it("requires an explicit reviewer identity", () => {
    const decide = vi.fn();
    render(<ApprovalDialog action="approve" request={request} api={{ decide }} onClose={vi.fn()} onCompleted={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "Approve" }));
    expect(screen.getByRole("alert")).toHaveTextContent("Please enter your name.");
    expect(decide).not.toHaveBeenCalled();
  });

  it("approves with an optional comment", async () => {
    const decide = vi.fn().mockResolvedValue(request);
    const completed = vi.fn();
    render(<ApprovalDialog action="approve" request={request} api={{ decide }} onClose={vi.fn()} onCompleted={completed} />);
    fireEvent.change(screen.getByPlaceholderText("Add a comment..."), { target: { value: "Within policy" } });
    fireEvent.change(screen.getByLabelText("Reviewer name"), { target: { value: "Dana Reviewer" } });
    fireEvent.click(screen.getByRole("button", { name: "Approve" }));
    await waitFor(() => expect(decide).toHaveBeenCalledWith("request-1", expect.objectContaining({ action: "approve", reason: "Within policy", decidedBy: "Dana Reviewer" })));
    expect(completed).toHaveBeenCalled();
  });


  it("disables dialog actions while an approval is pending", async () => {
    let resolveDecision: ((value: PurchaseRequestDetail) => void) | undefined;
    const decide = vi.fn().mockImplementation(
      () => new Promise<PurchaseRequestDetail>((resolve) => { resolveDecision = resolve; }),
    );
    render(<ApprovalDialog action="approve" request={request} api={{ decide }} onClose={vi.fn()} onCompleted={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Reviewer name"), { target: { value: "Dana Reviewer" } });
    fireEvent.click(screen.getByRole("button", { name: "Approve" }));
    expect(screen.getByRole("button", { name: "Saving…" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Cancel" })).toBeDisabled();
    resolveDecision?.(request);
    await waitFor(() => expect(decide).toHaveBeenCalledTimes(1));
  });

  it("requires a rejection reason before calling the API", async () => {
    const decide = vi.fn();
    render(<ApprovalDialog action="reject" request={request} api={{ decide }} onClose={vi.fn()} onCompleted={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Reviewer name"), { target: { value: "Dana Reviewer" } });
    fireEvent.click(screen.getByRole("button", { name: "Reject" }));
    expect(screen.getByRole("alert")).toHaveTextContent("Please provide a reason");
    expect(decide).not.toHaveBeenCalled();
  });

  it("shows safe API errors and allows closing the dialog", async () => {
    const close = vi.fn();
    const decide = vi.fn().mockRejectedValue(new Error("Unable to update this request."));
    render(<ApprovalDialog action="approve" request={request} api={{ decide }} onClose={close} onCompleted={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Reviewer name"), { target: { value: "Dana Reviewer" } });
    fireEvent.click(screen.getByRole("button", { name: "Approve" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Unable to update this request.");
    fireEvent.click(screen.getByRole("button", { name: "Close dialog" }));
    expect(close).toHaveBeenCalled();
  });

  it("validates edited item descriptions before submission", () => {
    const decide = vi.fn();
    render(<ApprovalDialog action="edit" request={request} api={{ decide }} onClose={vi.fn()} onCompleted={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Item 1 description"), { target: { value: "   " } });
    fireEvent.change(screen.getByLabelText("Reviewer name"), { target: { value: "Dana Reviewer" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
    expect(screen.getByRole("alert")).toHaveTextContent("Each item needs a description");
    expect(decide).not.toHaveBeenCalled();
  });

  it("edits items and sends only editable trusted inputs", async () => {
    const decide = vi.fn().mockResolvedValue(request);
    render(<ApprovalDialog action="edit" request={request} api={{ decide } as PurchaseRequestApprovalApi} onClose={vi.fn()} onCompleted={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Item 1 quantity"), { target: { value: "3" } });
    fireEvent.change(screen.getByLabelText("Reviewer name"), { target: { value: "Dana Reviewer" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
    await waitFor(() => expect(decide).toHaveBeenCalledWith("request-1", expect.objectContaining({
      action: "edit",
      items: [{ description: "Laptop stand", quantity: 3 }],
    })));
  });
});
