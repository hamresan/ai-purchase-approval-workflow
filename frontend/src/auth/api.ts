import { ApiError } from "@/api/purchaseRequests";
import type { AuthSession } from "@/auth/session";

export type AuthPurpose = "registration" | "login";

export interface OtpChallenge {
  challengeId: string;
  resendAvailableAt: string;
}

export interface IdentityAuthApi {
  requestOtp(mobileNumber: string, purpose: AuthPurpose): Promise<OtpChallenge>;
  verifyOtp(challengeId: string, code: string, fullName?: string): Promise<AuthSession>;
}

export class HttpIdentityAuthApi implements IdentityAuthApi {
  constructor(private readonly baseUrl = "") {}

  async requestOtp(mobileNumber: string, purpose: AuthPurpose): Promise<OtpChallenge> {
    const response = await fetch(`${this.baseUrl}/identity/otp/request`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        identity_type: "mobile",
        destination: mobileNumber,
        purpose,
        locale: "en",
      }),
    });
    if (!response.ok) throw new ApiError(response.status, await readIdentityError(response));
    const payload = (await response.json()) as { challenge_id?: unknown; resend_available_at?: unknown };
    if (typeof payload.challenge_id !== "string" || typeof payload.resend_available_at !== "string") {
      throw new ApiError(502, "The server returned an invalid OTP response.");
    }
    return { challengeId: payload.challenge_id, resendAvailableAt: payload.resend_available_at };
  }

  async verifyOtp(challengeId: string, code: string, fullName?: string): Promise<AuthSession> {
    const response = await fetch(`${this.baseUrl}/identity/otp/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        challenge_id: challengeId,
        code,
        full_name: fullName || null,
      }),
    });
    if (!response.ok) throw new ApiError(response.status, await readIdentityError(response));
    const payload = (await response.json()) as Record<string, unknown>;
    if (
      typeof payload.user_id !== "string"
      || typeof payload.access_token !== "string"
      || typeof payload.refresh_token !== "string"
    ) {
      throw new ApiError(502, "The server returned an invalid authentication response.");
    }
    return {
      userId: payload.user_id,
      accessToken: payload.access_token,
      refreshToken: payload.refresh_token,
    };
  }
}

async function readIdentityError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    return typeof payload.detail === "string" ? payload.detail : "Unable to authenticate.";
  } catch {
    return "Unable to authenticate.";
  }
}
