interface AdminHttpClient { fetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> }

export interface Department { id: string; name: string; is_active: boolean }
export interface Product { id: string; name: string; is_active: boolean }
export interface Vendor { id: string; name: string; is_active: boolean }
export interface Offer { id: string; product_id: string; vendor_id: string; unit_price_amount: string; currency: string; available_quantity: number; is_active: boolean }
export interface Budget { id: string; owner_type: "USER" | "DEPARTMENT"; user_id: string | null; department_id: string | null; amount: string; currency: string; is_active: boolean }
export interface RoleAssignment { user_id: string; roles: string[] }

export class HttpAdminApi {
  constructor(private readonly http: AdminHttpClient) {}
  private async get<T>(path: string): Promise<T> {
    const response = await this.http.fetch(path);
    if (!response.ok) throw new Error("Unable to load administration data.");
    return response.json() as Promise<T>;
  }
  departments() { return this.get<Department[]>("/api/admin/departments"); }
  products() { return this.get<Product[]>("/api/admin/products"); }
  vendors() { return this.get<Vendor[]>("/api/admin/vendors"); }
  offers() { return this.get<Offer[]>("/api/admin/offers"); }
  budgets() { return this.get<Budget[]>("/api/admin/budgets"); }
  roles() { return this.get<RoleAssignment[]>("/api/admin/roles"); }
}
