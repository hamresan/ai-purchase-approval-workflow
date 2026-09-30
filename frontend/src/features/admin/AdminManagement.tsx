import { useEffect, useState } from "react";
import type { Budget, Department, Offer, Product, RoleAssignment, Vendor } from "@/api/admin";
import { HttpAdminApi } from "@/api/admin";

interface Props { api: HttpAdminApi }

export function AdminManagement({ api }: Props) {
  const [data, setData] = useState<{departments: Department[]; products: Product[]; vendors: Vendor[]; offers: Offer[]; budgets: Budget[]; roles: RoleAssignment[]} | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    void Promise.all([api.departments(), api.products(), api.vendors(), api.offers(), api.budgets(), api.roles()])
      .then(([departments, products, vendors, offers, budgets, roles]) => setData({ departments, products, vendors, offers, budgets, roles }))
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Unable to load administration data."));
  }, [api]);
  return <section className="page admin-page">
    <div className="page-heading"><div><h1>Admin Management</h1><p>Manage trusted purchasing data for your organization.</p></div></div>
    {error && <div className="admin-error" role="alert">{error}</div>}
    {!data && !error && <div className="state-panel"><h2>Loading administration data…</h2></div>}
    {data && <>
      <div className="admin-tabs"><span className="active">Users & Roles</span><span>Departments</span><span>Catalog & Vendors</span><span>Budgets</span></div>
      <div className="admin-grid">
        <AdminCard title="Users & roles"><AdminTable headers={["User ID", "Roles"]} rows={data.roles.map(item => [item.user_id, item.roles.join(", ")])} /></AdminCard>
        <AdminCard title="Departments"><AdminTable headers={["Department", "Status"]} rows={data.departments.map(item => [item.name, item.is_active ? "Active" : "Inactive"])} /></AdminCard>
        <AdminCard title="Products"><AdminTable headers={["Product", "Status"]} rows={data.products.map(item => [item.name, item.is_active ? "Active" : "Inactive"])} /></AdminCard>
        <AdminCard title="Vendors"><AdminTable headers={["Vendor", "Status"]} rows={data.vendors.map(item => [item.name, item.is_active ? "Active" : "Inactive"])} /></AdminCard>
        <AdminCard title="Trusted prices & availability"><AdminTable headers={["Product", "Vendor", "Price", "Available"]} rows={data.offers.map(item => [item.product_id, item.vendor_id, item.currency + " " + item.unit_price_amount, String(item.available_quantity)])} /></AdminCard>
        <AdminCard title="Budgets"><AdminTable headers={["Owner", "Currency", "Limit", "Status"]} rows={data.budgets.map(item => [item.owner_type === "USER" ? item.user_id ?? "—" : item.department_id ?? "—", item.currency, item.amount, item.is_active ? "Active" : "Inactive"])} /></AdminCard>
      </div>
    </>}
  </section>;
}
function AdminCard({ title, children }: { title: string; children: React.ReactNode }) { return <article className="admin-card"><h2>{title}</h2>{children}</article>; }
function AdminTable({ headers, rows }: { headers: string[]; rows: string[][] }) { return <div className="admin-table-wrap"><table className="admin-table"><thead><tr>{headers.map(value => <th key={value}>{value}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={index}>{row.map((value, cell) => <td key={cell}>{value}</td>)}</tr>)}</tbody></table></div>; }
