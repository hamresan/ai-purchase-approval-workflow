import { HttpIdentityAuthApi } from "@/auth/api";

const jsonHeaders = { "Content-Type": "application/json" };

describe("HttpIdentityAuthApi", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("requests a mobile OTP", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          challenge_id: "challenge-1",
          resend_available_at: "2026-09-28T12:00:00Z",
        }),
        { status: 202, headers: jsonHeaders },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      new HttpIdentityAuthApi("http://api.test").requestOtp("+96891234567", "login"),
    ).resolves.toEqual({
      challengeId: "challenge-1",
      resendAvailableAt: "2026-09-28T12:00:00Z",
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/identity/otp/request",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("verifies OTP and maps the session", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            user_id: "user-1",
            access_token: "access",
            refresh_token: "refresh",
          }),
          { status: 200, headers: jsonHeaders },
        ),
      ),
    );

    await expect(
      new HttpIdentityAuthApi().verifyOtp("challenge-1", "123456"),
    ).resolves.toEqual({
      userId: "user-1",
      accessToken: "access",
      refreshToken: "refresh",
    });
  });

  it("refreshes a session", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          user_id: "user-1",
          access_token: "new-access",
          refresh_token: "new-refresh",
        }),
        { status: 200, headers: jsonHeaders },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      new HttpIdentityAuthApi().refreshSession("refresh-token-value-12345678901234567890"),
    ).resolves.toEqual({
      userId: "user-1",
      accessToken: "new-access",
      refreshToken: "new-refresh",
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/identity/sessions/refresh",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("updates the authenticated user's profile", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      new HttpIdentityAuthApi().updateProfile("access-token", "Dana Example"),
    ).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/profile",
      expect.objectContaining({
        method: "PATCH",
        headers: expect.objectContaining({ Authorization: "Bearer access-token" }),
        body: JSON.stringify({ full_name: "Dana Example" }),
      }),
    );
  });

  it("revokes a refresh session", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      new HttpIdentityAuthApi().revokeSession("refresh-token"),
    ).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      "/identity/sessions/revoke",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ refresh_token: "refresh-token" }),
      }),
    );
  });

  it("surfaces identity API errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "OTP challenge expired." }), {
          status: 400,
          headers: jsonHeaders,
        }),
      ),
    );

    await expect(
      new HttpIdentityAuthApi().verifyOtp("challenge-1", "123456"),
    ).rejects.toMatchObject({
      status: 400,
      message: "OTP challenge expired.",
    });
  });

  it("rejects invalid auth responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({}), { status: 200, headers: jsonHeaders }),
      ),
    );

    await expect(
      new HttpIdentityAuthApi().verifyOtp("challenge-1", "123456"),
    ).rejects.toMatchObject({ status: 502 });
  });
});
