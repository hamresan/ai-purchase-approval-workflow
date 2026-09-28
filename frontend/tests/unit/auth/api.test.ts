import { HttpIdentityAuthApi } from "@/auth/api";
describe("HttpIdentityAuthApi", () => {
  afterEach(() => vi.unstubAllGlobals());
  it("requests a mobile OTP", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ challenge_id: "challenge-1", resend_available_at: "2026-09-28T12:00:00Z" }), { status: 202, headers: { "Content-Type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(new HttpIdentityAuthApi("http://api.test").requestOtp("+96891234567", "login")).resolves.toEqual({ challengeId: "challenge-1", resendAvailableAt: "2026-09-28T12:00:00Z" });
    expect(fetchMock).toHaveBeenCalledWith("http://api.test/identity/otp/request", expect.objectContaining({ method: "POST" }));
  });
  it("verifies OTP and maps the session", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ user_id: "user-1", access_token: "access", refresh_token: "refresh" }), { status: 200, headers: { "Content-Type": "application/json" } })));
    await expect(new HttpIdentityAuthApi().verifyOtp("challenge-1", "123456")).resolves.toEqual({ userId: "user-1", accessToken: "access", refreshToken: "refresh" });
  });
  it("rejects invalid auth responses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({}), { status: 200, headers: { "Content-Type": "application/json" } })));
    await expect(new HttpIdentityAuthApi().verifyOtp("challenge-1", "123456")).rejects.toMatchObject({ status: 502 });
  });
});
