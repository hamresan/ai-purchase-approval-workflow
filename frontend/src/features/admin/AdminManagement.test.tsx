import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AdminManagement } from "@/features/admin/AdminManagement";
import type { HttpAdminApi } from "@/api/admin";

describe("AdminManagement", () => {
  it("renders trusted administration data", async () => {
    const api = {
      departments: async () => [{ id: "d1", name: "Engineering", is_active: true }],
      products: async () => [{ id: "p1", name: "Laptop stand", is_active: true }],
      vendors: async () => [{ id: "v1", name: "Acme", is_active: true }],
      offers: async () => [{ id: "o1", product_id: "p1", vendor_id: "v1", unit_price_amount: "35.00", currency: "USD", available_quantity: 10, is_active: true }],
      budgets: async () => [{ id: "b1", owner_type: "DEPARTMENT" as const, user_id: null, department_id: "d1", amount: "500.00", currency: "USD", is_active: true }],
      roles: async () => [{ user_id: "u1", roles: ["admin"] }],
      replaceRoles: async (userId: string, roles: string[]) => ({ user_id: userId, roles }),
    } as HttpAdminApi;
    render(<AdminManagement api={api} />);
    await waitFor(() => expect(screen.getByText("Engineering")).toBeInTheDocument());
    expect(screen.getByText("Laptop stand")).toBeInTheDocument();
    expect(screen.getByText("Acme")).toBeInTheDocument();
    expect(screen.getByText("USD 35.00")).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: "Admin" })).toBeChecked();
  });
});
