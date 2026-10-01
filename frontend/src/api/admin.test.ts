import { HttpAdminApi } from "@/api/admin";

describe("HttpAdminApi", () => {
  it("loads all administration resources", async () => {
    const fetch = vi.fn().mockImplementation(() =>
      Promise.resolve(
        new Response(JSON.stringify([]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
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

  it("writes all administration resources", async () => {
    const fetch = vi.fn().mockImplementation((_input: RequestInfo | URL, init?: RequestInit) =>
      Promise.resolve(
        new Response(init?.body ?? JSON.stringify({}), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );
    const api = new HttpAdminApi({ fetch });

    await api.createDepartment("Engineering");
    await api.updateDepartment({ id: "d1", name: "Engineering", is_active: false });
    await api.saveProduct({ id: "p1", name: "Laptop stand", is_active: true });
    await api.saveVendor({ id: "v1", name: "Acme", is_active: true });
    await api.saveOffer({
      id: "o1",
      product_id: "p1",
      vendor_id: "v1",
      unit_price_amount: "35.00",
      currency: "USD",
      available_quantity: 10,
      is_active: true,
    });
    await api.saveBudget({
      id: "b1",
      owner_type: "DEPARTMENT",
      user_id: null,
      department_id: "d1",
      amount: "500.00",
      currency: "USD",
      is_active: true,
    });

    expect(fetch).toHaveBeenCalledTimes(6);
    expect(fetch).toHaveBeenCalledWith(
      "/api/admin/departments",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetch).toHaveBeenCalledWith(
      "/api/admin/products/p1",
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
