import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { IdentityAuthApi } from "@/auth/api";
import { AuthScreen } from "@/features/auth/AuthScreen";

describe("AuthScreen", () => {
  it("automatically verifies a complete six-digit OTP", async () => {
    const api: IdentityAuthApi = {
      requestOtp: vi.fn().mockResolvedValue({ challengeId: "challenge-1", resendAvailableAt: "2026-09-28T12:00:00Z" }),
      verifyOtp: vi.fn().mockResolvedValue({ userId: "user-1", accessToken: "access", refreshToken: "refresh" }),
    };
    const authenticated = vi.fn();
    render(<AuthScreen api={api} onAuthenticated={authenticated} />);
    fireEvent.change(screen.getByLabelText("Mobile number"), { target: { value: "+96891234567" } });
    fireEvent.click(screen.getByRole("button", { name: "Send OTP" }));
    await screen.findByRole("heading", { name: "Check your OTP" });

    for (const [index, digit] of [..."123456"].entries()) {
      fireEvent.change(screen.getByLabelText(`OTP digit ${index + 1}`), { target: { value: digit } });
    }

    await waitFor(() => expect(authenticated).toHaveBeenCalledWith({ userId: "user-1", accessToken: "access", refreshToken: "refresh" }));
    expect(api.verifyOtp).toHaveBeenCalledWith("challenge-1", "123456", undefined);
  });

  it("accepts a pasted six-digit OTP and verifies automatically", async () => {
    const api: IdentityAuthApi = {
      requestOtp: vi.fn().mockResolvedValue({ challengeId: "challenge-1", resendAvailableAt: "2026-09-28T12:00:00Z" }),
      verifyOtp: vi.fn().mockResolvedValue({ userId: "user-1", accessToken: "access", refreshToken: "refresh" }),
    };
    render(<AuthScreen api={api} onAuthenticated={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Mobile number"), { target: { value: "+96891234567" } });
    fireEvent.click(screen.getByRole("button", { name: "Send OTP" }));
    await screen.findByRole("heading", { name: "Check your OTP" });

    fireEvent.paste(screen.getByLabelText("OTP digit 1").parentElement!, {
      clipboardData: { getData: () => "123456" },
    });

    await waitFor(() => expect(api.verifyOtp).toHaveBeenCalledWith("challenge-1", "123456", undefined));
  });

  it("registers with a full name and supports returning to mobile entry", async () => {
    const api: IdentityAuthApi = {
      requestOtp: vi.fn().mockResolvedValue({ challengeId: "challenge-2", resendAvailableAt: "2026-09-28T12:00:00Z" }),
      verifyOtp: vi.fn().mockResolvedValue({ userId: "user-2", accessToken: "access", refreshToken: "refresh" }),
    };
    render(<AuthScreen api={api} onAuthenticated={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));
    fireEvent.change(screen.getByLabelText("Mobile number"), { target: { value: "+96892345678" } });
    fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "Dana" } });
    fireEvent.click(screen.getByRole("button", { name: "Send OTP" }));
    await screen.findByRole("heading", { name: "Check your OTP" });
    fireEvent.click(screen.getByRole("button", { name: "Change mobile number" }));
    expect(screen.getByRole("heading", { name: "Create your account" })).toBeInTheDocument();
  });
});
