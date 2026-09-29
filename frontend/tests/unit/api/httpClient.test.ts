import { AuthorizedHttpClient } from "@/api/httpClient";

describe("AuthorizedHttpClient", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("refreshes once after an unauthorized response and retries with the new token", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(null, { status: 401 }))
      .mockResolvedValueOnce(new Response("ok", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const provider = {
      getSession: vi.fn().mockReturnValue({ userId: "u1", accessToken: "old", refreshToken: "r1" }),
      refreshSession: vi.fn().mockResolvedValue({ userId: "u1", accessToken: "new", refreshToken: "r2" }),
      clearSession: vi.fn(),
    };

    const response = await new AuthorizedHttpClient(provider).fetch("/api/purchase-requests");

    expect(response.status).toBe(200);
    expect(provider.refreshSession).toHaveBeenCalledOnce();
    expect(new Headers(fetchMock.mock.calls[1][1].headers).get("Authorization")).toBe("Bearer new");
  });

  it("clears the session when refresh fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(null, { status: 401 })));
    const provider = {
      getSession: vi.fn().mockReturnValue({ userId: "u1", accessToken: "old", refreshToken: "r1" }),
      refreshSession: vi.fn().mockRejectedValue(new Error("expired")),
      clearSession: vi.fn(),
    };

    await expect(new AuthorizedHttpClient(provider).fetch("/api/purchase-requests")).rejects.toMatchObject({ status: 401 });
    expect(provider.clearSession).toHaveBeenCalledOnce();
  });
});
