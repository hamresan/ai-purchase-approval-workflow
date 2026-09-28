import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { IdentityAuthApi } from "@/auth/api";
import { AuthScreen } from "@/features/auth/AuthScreen";

describe("AuthScreen", () => {
  it("signs in with mobile OTP", async () => {
    const api: IdentityAuthApi = {
      requestOtp: vi.fn().mockResolvedValue({ challengeId: "challenge-1", resendAvailableAt: "2026-09-28T12:00:00Z" }),
      verifyOtp: vi.fn().mockResolvedValue({ userId: "user-1", accessToken: "access", refreshToken: "refresh" }),
    };
    const authenticated = vi.fn();
    render(<AuthScreen api={api} onAuthenticated={authenticated} />);
    fireEvent.change(screen.getByLabelText("Mobile number"), { target: { value: "+96891234567" } });
    fireEvent.click(screen.getByRole("button", { name: "Send OTP" }));
    await screen.findByRole("heading", { name: "Check your OTP" });
    fireEvent.change(screen.getByLabelText("Verification code"), { target: { value: "123456" } });
    fireEvent.click(screen.getByRole("button", { name: "Verify and continue" }));
    await waitFor(() => expect(authenticated).toHaveBeenCalledWith({ userId: "user-1", accessToken: "access", refreshToken: "refresh" }));
    expect(api.verifyOtp).toHaveBeenCalledWith("challenge-1", "123456", undefined);
  });
});
