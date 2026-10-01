import { useEffect, useState } from "react";
import type { Budget, Department, Offer, Product, RoleAssignment, Vendor } from "@/api/admin";
import { HttpAdminApi } from "@/api/admin";
import { RoleManagement } from "@/features/admin/RoleManagement";

interface Props { api: HttpAdminApi }
interface AdminData { departments: Department[]; products: Product[]; vendors: Vendor[]; offers: Offer[]; budgets: Budget[]; roles: RoleAssignment[] }

export function AdminManagement({ api }: Props) {
  const [data, setData] = useState<AdminData | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    void loadData(api).then(setData).catch((reason: unknown) =>
      setError(reason instanceof Error ? reason.message : "Unable to load administration data."));
  }, [api]);

  const reload = async () => {
    setError("");
    try { setData(await loadData(api)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load administration data."); }
  };

  return <section className="page admin-page">
    <div className="page-heading"><div><h1>Admin Management</h1><p>Manage trusted purchasing data for your organization.</p></div></div>
    {error && <div className="admin-error" role="alert">{error}</div>}
    {!data && !error && <div className="state-panel"><h2>Loading administration data…</h2></div>}
    {data && <>
      <div className="admin-tabs"><span className="active">Users & Roles</span><span>Departments</span><span>Catalog & Vendors</span><span>Budgets</span></div>
      <div className="admin-grid">
        <AdminCard title="Users & roles"><RoleManagement api={api} assignments={data.roles} onChanged={roles => setData(current => current ? { ...current, roles } : current)} /></AdminCard>
        <AdminCard title="Departments"><NamedEditor kind="Department" items={data.departments} create={name => api.createDepartment(name)} save={item => api.updateDepartment(item)} reload={reload} /></AdminCard>
        <AdminCard title="Products"><NamedEditor kind="Product" items={data.products} create={name => api.saveProduct({ id: crypto.randomUUID(), name, is_active: true })} save={item => api.saveProduct(item)} reload={reload} /></AdminCard>
        <AdminCard title="Vendors"><NamedEditor kind="Vendor" items={data.vendors} create={name => api.saveVendor({ id: crypto.randomUUID(), name, is_active: true })} save={item => api.saveVendor(item)} reload={reload} /></AdminCard>
        <AdminCard title="Trusted prices & availability"><OfferEditor api={api} data={data} reload={reload} /></AdminCard>
        <AdminCard title="Budgets"><BudgetEditor api={api} data={data} reload={reload} /></AdminCard>
      </div>
    </>}
  </section>;
}

async function loadData(api: HttpAdminApi): Promise<AdminData> {
  const [departments, products, vendors, offers, budgets, roles] = await Promise.all([
    api.departments(), api.products(), api.vendors(), api.offers(), api.budgets(), api.roles(),
  ]);
  return { departments, products, vendors, offers, budgets, roles };
}

function AdminCard({ title, children }: { title: string; children: React.ReactNode }) {
  return <article className="admin-card"><h2>{title}</h2>{children}</article>;
}

function NamedEditor<T extends { id: string; name: string; is_active: boolean }>({ kind, items, create, save, reload }: {
  kind: string; items: T[]; create: (name: string) => Promise<unknown>; save: (item: T) => Promise<unknown>; reload: () => Promise<void>;
}) {
  const [name, setName] = useState("");
  const submit = async () => { if (!name.trim()) return; await create(name.trim()); setName(""); await reload(); };
  return <><div className="admin-inline-form"><input aria-label={`New ${kind}`} placeholder={`New ${kind.toLowerCase()} name`} value={name} onChange={event => setName(event.target.value)} /><button className="primary-button" onClick={() => void submit()}>Add</button></div>
    <div className="admin-table-wrap"><table className="admin-table"><thead><tr><th>{kind}</th><th>Status</th><th>Action</th></tr></thead><tbody>
      {items.map(item => <tr key={item.id}><td>{item.name}</td><td>{item.is_active ? "Active" : "Inactive"}</td><td><button className="admin-link-button" onClick={() => void save({ ...item, is_active: !item.is_active }).then(reload)}>{item.is_active ? "Deactivate" : "Activate"}</button></td></tr>)}
    </tbody></table></div></>;
}

function OfferEditor({ api, data, reload }: { api: HttpAdminApi; data: AdminData; reload: () => Promise<void> }) {
  const [productId, setProductId] = useState(""); const [vendorId, setVendorId] = useState("");
  const [price, setPrice] = useState(""); const [currency, setCurrency] = useState("USD"); const [quantity, setQuantity] = useState("0");
  const add = async () => {
    if (!productId || !vendorId || !price) return;
    await api.saveOffer({ id: crypto.randomUUID(), product_id: productId, vendor_id: vendorId, unit_price_amount: price, currency, available_quantity: Number(quantity), is_active: true });
    setPrice(""); setQuantity("0"); await reload();
  };
  const names = (id: string, values: Array<Product | Vendor>) => values.find(item => item.id === id)?.name ?? id;
  return <><div className="admin-resource-form">
    <select aria-label="Product" value={productId} onChange={e => setProductId(e.target.value)}><option value="">Product</option>{data.products.filter(x => x.is_active).map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select>
    <select aria-label="Vendor" value={vendorId} onChange={e => setVendorId(e.target.value)}><option value="">Vendor</option>{data.vendors.filter(x => x.is_active).map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select>
    <input aria-label="Price" type="number" min="0.01" step="0.01" placeholder="Price" value={price} onChange={e => setPrice(e.target.value)} />
    <input aria-label="Currency" maxLength={3} value={currency} onChange={e => setCurrency(e.target.value.toUpperCase())} />
    <input aria-label="Available quantity" type="number" min="0" value={quantity} onChange={e => setQuantity(e.target.value)} />
    <button className="primary-button" onClick={() => void add()}>Add offer</button>
  </div><div className="admin-table-wrap"><table className="admin-table"><thead><tr><th>Product</th><th>Vendor</th><th>Price</th><th>Available</th><th>Action</th></tr></thead><tbody>
    {data.offers.map(item => <tr key={item.id}><td>{names(item.product_id, data.products)}</td><td>{names(item.vendor_id, data.vendors)}</td><td>{item.currency} {item.unit_price_amount}</td><td>{item.available_quantity}</td><td><button className="admin-link-button" onClick={() => void api.saveOffer({ ...item, is_active: !item.is_active }).then(reload)}>{item.is_active ? "Deactivate" : "Activate"}</button></td></tr>)}
  </tbody></table></div></>;
}

function BudgetEditor({ api, data, reload }: { api: HttpAdminApi; data: AdminData; reload: () => Promise<void> }) {
  const [ownerType, setOwnerType] = useState<"USER" | "DEPARTMENT">("DEPARTMENT"); const [ownerId, setOwnerId] = useState("");
  const [amount, setAmount] = useState(""); const [currency, setCurrency] = useState("USD");
  const add = async () => {
    if (!ownerId || !amount) return;
    await api.saveBudget({ id: crypto.randomUUID(), owner_type: ownerType, user_id: ownerType === "USER" ? ownerId : null, department_id: ownerType === "DEPARTMENT" ? ownerId : null, amount, currency, is_active: true });
    setAmount(""); await reload();
  };
  return <><div className="admin-resource-form">
    <select aria-label="Budget owner type" value={ownerType} onChange={e => { setOwnerType(e.target.value as "USER" | "DEPARTMENT"); setOwnerId(""); }}><option value="DEPARTMENT">Department</option><option value="USER">User</option></select>
    {ownerType === "DEPARTMENT" ? <select aria-label="Budget owner" value={ownerId} onChange={e => setOwnerId(e.target.value)}><option value="">Department</option>{data.departments.filter(x => x.is_active).map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select> : <select aria-label="Budget owner" value={ownerId} onChange={e => setOwnerId(e.target.value)}><option value="">User</option>{data.roles.map(x => <option key={x.user_id} value={x.user_id}>{x.user_id}</option>)}</select>}
    <input aria-label="Budget amount" type="number" min="0.01" step="0.01" placeholder="Limit" value={amount} onChange={e => setAmount(e.target.value)} />
    <input aria-label="Budget currency" maxLength={3} value={currency} onChange={e => setCurrency(e.target.value.toUpperCase())} />
    <button className="primary-button" onClick={() => void add()}>Add budget</button>
  </div><div className="admin-table-wrap"><table className="admin-table"><thead><tr><th>Owner</th><th>Currency</th><th>Limit</th><th>Status</th><th>Action</th></tr></thead><tbody>
    {data.budgets.map(item => <tr key={item.id}><td>{item.owner_type === "USER" ? item.user_id : data.departments.find(x => x.id === item.department_id)?.name ?? item.department_id}</td><td>{item.currency}</td><td>{item.amount}</td><td>{item.is_active ? "Active" : "Inactive"}</td><td><button className="admin-link-button" onClick={() => void api.saveBudget({ ...item, is_active: !item.is_active }).then(reload)}>{item.is_active ? "Deactivate" : "Activate"}</button></td></tr>)}
  </tbody></table></div></>;
}
