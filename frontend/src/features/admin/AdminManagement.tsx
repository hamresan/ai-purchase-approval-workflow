import { useEffect, useState } from "react";
import type { HttpAdminApi } from "@/api/admin";
import { AdminTabs } from "@/features/admin/AdminTabs";
import { BudgetEditor } from "@/features/admin/BudgetEditor";
import { NamedResourceEditor } from "@/features/admin/NamedResourceEditor";
import { OfferEditor } from "@/features/admin/OfferEditor";
import { RoleManagement } from "@/features/admin/RoleManagement";
import type { AdminData, AdminTab } from "@/features/admin/types";

interface Props { api: HttpAdminApi }

export function AdminManagement({ api }: Props) {
  const [data, setData] = useState<AdminData | null>(null);
  const [activeTab, setActiveTab] = useState<AdminTab>("roles");
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
      <AdminTabs active={activeTab} onChange={setActiveTab} />
      <div className="admin-tab-content">
        {activeTab === "roles" && <AdminCard title="Users & roles">
          <RoleManagement api={api} assignments={data.roles}
            onChanged={roles => setData(current => current ? { ...current, roles } : current)} />
        </AdminCard>}
        {activeTab === "departments" && <AdminCard title="Departments">
          <NamedResourceEditor kind="Department" items={data.departments}
            create={name => api.createDepartment(name)} save={item => api.updateDepartment(item)} reload={reload} onError={setError} />
        </AdminCard>}
        {activeTab === "catalog" && <div className="admin-grid">
          <AdminCard title="Products"><NamedResourceEditor kind="Product" items={data.products}
            create={name => api.createProduct(name)} save={item => api.saveProduct(item)} reload={reload} onError={setError} /></AdminCard>
          <AdminCard title="Vendors"><NamedResourceEditor kind="Vendor" items={data.vendors}
            create={name => api.createVendor(name)} save={item => api.saveVendor(item)} reload={reload} onError={setError} /></AdminCard>
          <AdminCard title="Trusted prices & availability" wide><OfferEditor api={api} data={data} reload={reload} onError={setError} /></AdminCard>
        </div>}
        {activeTab === "budgets" && <AdminCard title="Budgets">
          <BudgetEditor api={api} data={data} reload={reload} onError={setError} />
        </AdminCard>}
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

function AdminCard({ title, children, wide = false }: { title: string; children: React.ReactNode; wide?: boolean }) {
  return <article className={`admin-card${wide ? " admin-card-wide" : ""}`}><h2>{title}</h2>{children}</article>;
}
