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

  private put<T>(path: string, body: unknown, errorMessage = "Unable to update administration data."): Promise<T> {
    return this.request<T>(path, errorMessage, {
      method: "PUT",
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
    return this.put<Department>(`/api/admin/departments/${item.id}`, {
      name: item.name,
      is_active: item.is_active,
    });
  }

  saveProduct(item: Product): Promise<Product> {
    return this.put<Product>(`/api/admin/products/${item.id}`, item);
  }

  saveVendor(item: Vendor): Promise<Vendor> {
    return this.put<Vendor>(`/api/admin/vendors/${item.id}`, item);
  }

  saveOffer(item: Offer): Promise<Offer> {
    return this.put<Offer>(`/api/admin/offers/${item.id}`, item);
  }

  saveBudget(item: Budget): Promise<Budget> {
    return this.put<Budget>(`/api/admin/budgets/${item.id}`, item);
  }

  replaceRoles(userId: string, roles: string[]): Promise<RoleAssignment> {
    return this.put<RoleAssignment>(
      `/api/admin/roles/${encodeURIComponent(userId)}`,
      { roles },
      "Unable to update user roles.",
    );
  }
}
