import { ApiError } from "@/api/purchaseRequests";

export interface AccessTokenProvider {
  getAccessToken(): string | null;
}

export class AuthorizedHttpClient {
  constructor(private readonly tokenProvider: AccessTokenProvider) {}

  async fetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
    const accessToken = this.tokenProvider.getAccessToken();
    if (!accessToken) throw new ApiError(401, "Authentication is required.");
    const headers = new Headers(init.headers);
    headers.set("Authorization", `Bearer ${accessToken}`);
    return fetch(input, { ...init, headers });
  }
}
