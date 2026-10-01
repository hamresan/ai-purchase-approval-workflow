import { HttpAdminApi } from "@/api/admin";

describe("HttpAdminApi", () => {
  it("loads all administration resources", async () => {
    const fetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify([]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    const api = new HttpAdminApi({ fetch });

    await Promise.all([
      api.departments(),
      api.products(),
      api.vendors(),
      api.offers(),
      api.budgets(),
      api.roles(),
    ]);

    expect(fetch).toHaveBeenCalledTimes(6);
  });

  it("reports failed administration reads", async () => {
    const api = new HttpAdminApi({
      fetch: vi.fn().mockResolvedValue(new Response(null, { status: 500 })),
    });

    await expect(api.products()).rejects.toThrow("Unable to load administration data.");
  });

  it("replaces application roles", async () => {
    const assignment = { user_id: "user-1", roles: ["admin"] };
    const fetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(assignment), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    const api = new HttpAdminApi({ fetch });

    await expect(api.replaceRoles("user-1", ["admin"])).resolves.toEqual(assignment);
    expect(fetch).toHaveBeenCalledWith(
      "/api/admin/roles/user-1",
      expect.objectContaining({ method: "PUT" }),
    );
  });

  it("reports failed role updates", async () => {
    const api = new HttpAdminApi({
      fetch: vi.fn().mockResolvedValue(new Response(null, { status: 403 })),
    });

    await expect(api.replaceRoles("user-1", ["admin"])).rejects.toThrow(
      "Unable to update user roles.",
    );
  });
});
