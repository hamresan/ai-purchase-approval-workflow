import { ApiError } from "@/api/purchaseRequests";
import type { AuthSession } from "@/auth/session";

export interface SessionProvider {
  getSession(): AuthSession | null;
  refreshSession(): Promise<AuthSession>;
  clearSession(): void;
}

export class AuthorizedHttpClient {
  private refreshInFlight: Promise<AuthSession> | null = null;

  constructor(private readonly sessionProvider: SessionProvider) {}

  async fetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
    const session = this.sessionProvider.getSession();
    if (!session) throw new ApiError(401, "Authentication is required.");

    const response = await fetch(input, this.authorizedInit(init, session.accessToken));
    if (response.status !== 401) return response;

    try {
      const refreshed = await this.refresh();
      return await fetch(input, this.authorizedInit(init, refreshed.accessToken));
    } catch {
      this.sessionProvider.clearSession();
      throw new ApiError(401, "Your session has expired. Please sign in again.");
    }
  }

  private refresh(): Promise<AuthSession> {
    if (!this.refreshInFlight) {
      this.refreshInFlight = this.sessionProvider.refreshSession().finally(() => {
        this.refreshInFlight = null;
      });
    }
    return this.refreshInFlight;
  }

  private authorizedInit(init: RequestInit, accessToken: string): RequestInit {
    const headers = new Headers(init.headers);
    headers.set("Authorization", `Bearer ${accessToken}`);
    return { ...init, headers };
  }
}
