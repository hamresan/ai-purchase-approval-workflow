import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import type { IdentityAuthApi } from "@/auth/api";
import { AuthScreen } from "@/features/auth/AuthScreen";

function authApi(): IdentityAuthApi {
  return {
    requestOtp: vi.fn().mockResolvedValue({ challengeId: "challenge-1", resendAvailableAt: "2026-09-28T12:00:00Z" }),
    verifyOtp: vi.fn().mockResolvedValue({ userId: "user-1", accessToken: "access", refreshToken: "refresh" }),
    refreshSession: vi.fn(),
    revokeSession: vi.fn(),
    updateProfile: vi.fn().mockResolvedValue(undefined),
  };
}

describe("AuthScreen", () => {
  it("automatically verifies a complete six-digit OTP", async () => {
    const api = authApi();
    const authenticated = vi.fn();
    render(<AuthScreen api={api} onAuthenticated={authenticated} />);
    fireEvent.change(screen.getByLabelText("Mobile number"), { target: { value: "+96891234567" } });
    fireEvent.click(screen.getByRole("button", { name: "Send OTP" }));
    await screen.findByRole("heading", { name: "Check your OTP" });

    for (let index = 1; index <= 6; index += 1) {
      fireEvent.change(screen.getByLabelText(`OTP digit ${index}`), { target: { value: String(index) } });
    }

    await waitFor(() => expect(api.verifyOtp).toHaveBeenCalledWith("challenge-1", "123456", undefined));
    await waitFor(() => expect(authenticated).toHaveBeenCalled());
  });

  it("verifies a pasted six-digit OTP", async () => {
    const api = authApi();
    render(<AuthScreen api={api} onAuthenticated={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Mobile number"), { target: { value: "+96891234567" } });
    fireEvent.click(screen.getByRole("button", { name: "Send OTP" }));
    await screen.findByRole("heading", { name: "Check your OTP" });

    fireEvent.paste(screen.getByLabelText("OTP digit 1").parentElement!, {
      clipboardData: { getData: () => "123456" },
    });

    await waitFor(() => expect(api.verifyOtp).toHaveBeenCalledWith("challenge-1", "123456", undefined));
  });

  it("collects the registration profile after OTP verification", async () => {
    const api = authApi();
    const authenticated = vi.fn();
    render(<AuthScreen api={api} onAuthenticated={authenticated} />);
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));
    fireEvent.change(screen.getByLabelText("Mobile number"), { target: { value: "+96892345678" } });
    fireEvent.click(screen.getByRole("button", { name: "Send OTP" }));
    await screen.findByRole("heading", { name: "Check your OTP" });
    fireEvent.paste(screen.getByLabelText("OTP digit 1").parentElement!, {
      clipboardData: { getData: () => "123456" },
    });

    await waitFor(() => expect(api.verifyOtp).toHaveBeenCalledWith("challenge-1", "123456", "New user"));
    await screen.findByRole("heading", { name: "Set up your profile" });
    expect(authenticated).not.toHaveBeenCalled();
    fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "Dana" } });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() => expect(api.updateProfile).toHaveBeenCalledWith("access", "Dana"));
    await waitFor(() => expect(authenticated).toHaveBeenCalled());
  });
});
