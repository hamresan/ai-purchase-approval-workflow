import type { Budget, Department, Offer, Product, RoleAssignment, Vendor } from "@/api/admin";

export interface AdminData {
  departments: Department[];
  products: Product[];
  vendors: Vendor[];
  offers: Offer[];
  budgets: Budget[];
  roles: RoleAssignment[];
}

export type AdminTab = "roles" | "departments" | "catalog" | "budgets";
