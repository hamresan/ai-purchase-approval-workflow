import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AdminManagement } from "@/features/admin/AdminManagement";
import type { HttpAdminApi } from "@/api/admin";

function buildApi(overrides: Partial<HttpAdminApi> = {}): HttpAdminApi {
  return {
    departments: vi.fn().mockResolvedValue([{ id: "d1", name: "Engineering", is_active: true }]),
    products: vi.fn().mockResolvedValue([{ id: "p1", name: "Laptop stand", is_active: true }]),
    vendors: vi.fn().mockResolvedValue([{ id: "v1", name: "Acme", is_active: true }]),
    offers: vi.fn().mockResolvedValue([{ id: "o1", product_id: "p1", vendor_id: "v1", unit_price_amount: "35.00", currency: "USD", available_quantity: 10, is_active: true }]),
    budgets: vi.fn().mockResolvedValue([{ id: "b1", owner_type: "DEPARTMENT", user_id: null, department_id: "d1", amount: "500.00", currency: "USD", is_active: true }]),
    roles: vi.fn().mockResolvedValue([{ user_id: "u1", roles: ["admin"] }]),
    replaceRoles: vi.fn().mockResolvedValue({ user_id: "u1", roles: ["admin"] }),
    createDepartment: vi.fn().mockResolvedValue({ id: "d2", name: "Finance", is_active: true }),
    updateDepartment: vi.fn().mockResolvedValue({ id: "d1", name: "Engineering", is_active: false }),
    createProduct: vi.fn().mockResolvedValue({}),
    saveProduct: vi.fn().mockResolvedValue({}),
    createVendor: vi.fn().mockResolvedValue({}),
    saveVendor: vi.fn().mockResolvedValue({}),
    createOffer: vi.fn().mockResolvedValue({}),
    saveOffer: vi.fn().mockResolvedValue({}),
    createBudget: vi.fn().mockResolvedValue({}),
    saveBudget: vi.fn().mockResolvedValue({}),
    ...overrides,
  } as unknown as HttpAdminApi;
}

async function renderAdmin(api = buildApi()) {
  render(<AdminManagement api={api} />);
  await screen.findByRole("heading", { name: "Users & roles" });
  return api;
}

describe("AdminManagement", () => {
  it("renders trusted administration data", async () => {
    await renderAdmin();
    expect(screen.getByRole("checkbox", { name: "Admin" })).toBeChecked();
    expect(screen.queryByText("Engineering")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("tab", { name: "Departments" }));
    expect(screen.getByText("Engineering")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("tab", { name: "Catalog & Vendors" }));
    expect(screen.getAllByText("Laptop stand").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Acme").length).toBeGreaterThan(0);
    expect(screen.getByText("USD 35.00")).toBeInTheDocument();
  });

  it("creates a department and reloads data", async () => {
    const api = await renderAdmin();
    fireEvent.click(screen.getByRole("tab", { name: "Departments" }));
    fireEvent.change(screen.getByLabelText("New Department"), { target: { value: "Finance" } });
    fireEvent.click(screen.getAllByRole("button", { name: "Add" })[0]);
    await waitFor(() => expect(api.createDepartment).toHaveBeenCalledWith("Finance"));
    await waitFor(() => expect(api.departments).toHaveBeenCalledTimes(2));
  });

  it("deactivates named resources", async () => {
    const api = await renderAdmin();
    fireEvent.click(screen.getByRole("tab", { name: "Departments" }));
    fireEvent.click(screen.getByRole("button", { name: "Deactivate" }));
    fireEvent.click(screen.getByRole("tab", { name: "Catalog & Vendors" }));
    const buttons = screen.getAllByRole("button", { name: "Deactivate" });
    fireEvent.click(buttons[0]);
    fireEvent.click(buttons[1]);
    await waitFor(() => expect(api.updateDepartment).toHaveBeenCalled());
    await waitFor(() => expect(api.saveProduct).toHaveBeenCalled());
    await waitFor(() => expect(api.saveVendor).toHaveBeenCalled());
  });

  it("creates an offer and budget", async () => {
    const api = await renderAdmin();
    fireEvent.click(screen.getByRole("tab", { name: "Catalog & Vendors" }));
    fireEvent.change(screen.getByLabelText("Product"), { target: { value: "p1" } });
    fireEvent.change(screen.getByLabelText("Vendor"), { target: { value: "v1" } });
    fireEvent.change(screen.getByLabelText("Price"), { target: { value: "40" } });
    fireEvent.click(screen.getByRole("button", { name: "Add offer" }));
    await waitFor(() => expect(api.createOffer).toHaveBeenCalled());

    fireEvent.click(screen.getByRole("tab", { name: "Budgets" }));
    fireEvent.change(screen.getByLabelText("Budget owner"), { target: { value: "d1" } });
    fireEvent.change(screen.getByLabelText("Budget amount"), { target: { value: "900" } });
    fireEvent.click(screen.getByRole("button", { name: "Add budget" }));
    await waitFor(() => expect(api.createBudget).toHaveBeenCalled());
  });

  it("supports user budgets and active-state mutations", async () => {
    const api = await renderAdmin();
    fireEvent.click(screen.getByRole("tab", { name: "Budgets" }));
    fireEvent.change(screen.getByLabelText("Budget owner type"), { target: { value: "USER" } });
    fireEvent.change(screen.getByLabelText("Budget owner"), { target: { value: "u1" } });
    fireEvent.change(screen.getByLabelText("Budget amount"), { target: { value: "250" } });
    fireEvent.click(screen.getByRole("button", { name: "Add budget" }));
    await waitFor(() => expect(api.createBudget).toHaveBeenCalled());

    fireEvent.click(screen.getByRole("button", { name: "Deactivate" }));
    await waitFor(() => expect(api.saveBudget).toHaveBeenCalledTimes(1));
    fireEvent.click(screen.getByRole("tab", { name: "Catalog & Vendors" }));
    const catalogButtons = screen.getAllByRole("button", { name: "Deactivate" });
    fireEvent.click(catalogButtons[2]);
    await waitFor(() => expect(api.saveOffer).toHaveBeenCalledTimes(1));
  });


  it("edits named resources, offers, and budgets", async () => {
    const api = await renderAdmin();

    fireEvent.click(screen.getByRole("tab", { name: "Departments" }));
    fireEvent.click(screen.getByRole("button", { name: "Edit" }));
    fireEvent.change(screen.getByLabelText("Edit Department name"), { target: { value: "Operations" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
    await waitFor(() => expect(api.updateDepartment).toHaveBeenCalledWith(
      expect.objectContaining({ id: "d1", name: "Operations" }),
    ));

    fireEvent.click(screen.getByRole("tab", { name: "Catalog & Vendors" }));
    const editButtons = screen.getAllByRole("button", { name: "Edit" });
    fireEvent.click(editButtons[0]);
    fireEvent.change(screen.getByLabelText("Edit Product name"), { target: { value: "Monitor stand" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
    await waitFor(() => expect(api.saveProduct).toHaveBeenCalledWith(
      expect.objectContaining({ id: "p1", name: "Monitor stand" }),
    ));

    fireEvent.click(screen.getAllByRole("button", { name: "Edit" })[2]);
    fireEvent.change(screen.getByLabelText("Edit offer price"), { target: { value: "42.50" } });
    fireEvent.change(screen.getByLabelText("Edit offer available quantity"), { target: { value: "12" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
    await waitFor(() => expect(api.saveOffer).toHaveBeenCalledWith(
      expect.objectContaining({ id: "o1", unit_price_amount: "42.50", available_quantity: 12 }),
    ));

    fireEvent.click(screen.getByRole("tab", { name: "Budgets" }));
    fireEvent.click(screen.getByRole("button", { name: "Edit" }));
    fireEvent.change(screen.getByLabelText("Edit budget amount"), { target: { value: "750" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
    await waitFor(() => expect(api.saveBudget).toHaveBeenCalledWith(
      expect.objectContaining({ id: "b1", amount: "750" }),
    ));
  });


  it("covers edit cancellation and alternate edit fields", async () => {
    const api = await renderAdmin();

    fireEvent.click(screen.getByRole("tab", { name: "Departments" }));
    fireEvent.click(screen.getByRole("button", { name: "Edit" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Edit" }));
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("tab", { name: "Catalog & Vendors" }));
    fireEvent.click(screen.getAllByRole("button", { name: "Edit" })[1]);
    fireEvent.change(screen.getByLabelText("Edit Vendor name"), { target: { value: "Acme Updated" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
    await waitFor(() => expect(api.saveVendor).toHaveBeenCalledWith(
      expect.objectContaining({ id: "v1", name: "Acme Updated" }),
    ));

    fireEvent.click(screen.getAllByRole("button", { name: "Edit" })[2]);
    fireEvent.change(screen.getByLabelText("Edit offer product"), { target: { value: "p1" } });
    fireEvent.change(screen.getByLabelText("Edit offer vendor"), { target: { value: "v1" } });
    fireEvent.change(screen.getByLabelText("Edit offer currency"), { target: { value: "eur" } });
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("tab", { name: "Budgets" }));
    fireEvent.click(screen.getByRole("button", { name: "Edit" }));
    fireEvent.change(screen.getByLabelText("Edit budget owner"), { target: { value: "d1" } });
    fireEvent.change(screen.getByLabelText("Edit budget currency"), { target: { value: "eur" } });
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("edits a user-owned budget", async () => {
    const api = buildApi({
      budgets: vi.fn().mockResolvedValue([{
        id: "b2", owner_type: "USER", user_id: "u1", department_id: null,
        amount: "250.00", currency: "USD", is_active: true,
      }]),
    });
    await renderAdmin(api);
    fireEvent.click(screen.getByRole("tab", { name: "Budgets" }));
    fireEvent.click(screen.getByRole("button", { name: "Edit" }));
    fireEvent.change(screen.getByLabelText("Edit budget owner"), { target: { value: "u1" } });
    fireEvent.change(screen.getByLabelText("Edit budget currency"), { target: { value: "omr" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
    await waitFor(() => expect(api.saveBudget).toHaveBeenCalledWith(
      expect.objectContaining({
        id: "b2", owner_type: "USER", user_id: "u1", department_id: null, currency: "OMR",
      }),
    ));
  });

  it("shows loading failures", async () => {
    const api = buildApi({
      departments: vi.fn().mockRejectedValue(new Error("Admin unavailable")),
    } as Partial<HttpAdminApi>);
    render(<AdminManagement api={api} />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Admin unavailable");
  });
});
