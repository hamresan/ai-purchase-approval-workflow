interface AdminHttpClient { fetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> }

export interface Department { id: string; name: string; is_active: boolean }
export interface Product { id: string; name: string; is_active: boolean }
export interface Vendor { id: string; name: string; is_active: boolean }
export interface Offer { id: string; product_id: string; vendor_id: string; unit_price_amount: string; currency: string; available_quantity: number; is_active: boolean }
export interface Budget { id: string; owner_type: "USER" | "DEPARTMENT"; user_id: string | null; department_id: string | null; amount: string; currency: string; is_active: boolean }
export interface RoleAssignment { user_id: string; roles: string[] }

export class HttpAdminApi {
  constructor(private readonly http: AdminHttpClient) {}

  private async request<T>(path: string, errorMessage: string, init?: RequestInit): Promise<T> {
    const response = await this.http.fetch(path, init);
    if (!response.ok) throw new Error(errorMessage);
    return response.json() as Promise<T>;
  }

  private get<T>(path: string): Promise<T> {
    return this.request<T>(path, "Unable to load administration data.");
  }

  private write<T>(method: "POST" | "PUT", path: string, body: unknown, errorMessage = "Unable to update administration data."): Promise<T> {
    return this.request<T>(path, errorMessage, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }

  departments() { return this.get<Department[]>("/api/admin/departments"); }
  products() { return this.get<Product[]>("/api/admin/products"); }
  vendors() { return this.get<Vendor[]>("/api/admin/vendors"); }
  offers() { return this.get<Offer[]>("/api/admin/offers"); }
  budgets() { return this.get<Budget[]>("/api/admin/budgets"); }
  roles() { return this.get<RoleAssignment[]>("/api/admin/roles"); }

  createDepartment(name: string): Promise<Department> {
    return this.request<Department>(
      "/api/admin/departments",
      "Unable to update administration data.",
      {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
      },
    );
  }

  updateDepartment(item: Department): Promise<Department> {
    return this.write<Department>("PUT", `/api/admin/departments/${item.id}`, {
      name: item.name,
      is_active: item.is_active,
    });
  }

  createProduct(name: string): Promise<Product> {\n    return this.write<Product>("POST", "/api/admin/products", { name });\n  }\n\n  saveProduct(item: Product): Promise<Product> {\n    return this.write<Product>("PUT", `/api/admin/products/${item.id}`, { name: item.name, is_active: item.is_active });\n  }

  createVendor(name: string): Promise<Vendor> {\n    return this.write<Vendor>("POST", "/api/admin/vendors", { name });\n  }\n\n  saveVendor(item: Vendor): Promise<Vendor> {\n    return this.write<Vendor>("PUT", `/api/admin/vendors/${item.id}`, { name: item.name, is_active: item.is_active });\n  }

  createOffer(item: Omit<Offer, "id">): Promise<Offer> {\n    return this.write<Offer>("POST", "/api/admin/offers", item);\n  }\n\n  saveOffer(item: Offer): Promise<Offer> {\n    const { id, ...body } = item;\n    return this.write<Offer>("PUT", `/api/admin/offers/${id}`, body);\n  }

  createBudget(item: Omit<Budget, "id">): Promise<Budget> {\n    return this.write<Budget>("POST", "/api/admin/budgets", item);\n  }\n\n  saveBudget(item: Budget): Promise<Budget> {\n    const { id, ...body } = item;\n    return this.write<Budget>("PUT", `/api/admin/budgets/${id}`, body);\n  }

  replaceRoles(userId: string, roles: string[]): Promise<RoleAssignment> {
    return this.write<RoleAssignment>("PUT",
      `/api/admin/roles/${encodeURIComponent(userId)}`,
      { roles },
      "Unable to update user roles.",
    );
  }
}
