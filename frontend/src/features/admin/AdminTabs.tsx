import type { AdminTab } from "@/features/admin/types";

const TABS: Array<{ id: AdminTab; label: string }> = [
  { id: "roles", label: "Users & Roles" },
  { id: "departments", label: "Departments" },
  { id: "catalog", label: "Catalog & Vendors" },
  { id: "budgets", label: "Budgets" },
];

export function AdminTabs({ active, onChange }: { active: AdminTab; onChange: (tab: AdminTab) => void }) {
  return <div className="admin-tabs" role="tablist" aria-label="Administration sections">
    {TABS.map(tab => <button key={tab.id} type="button" role="tab" aria-selected={active === tab.id}
      className={active === tab.id ? "active" : ""} onClick={() => onChange(tab.id)}>
      {tab.label}
    </button>)}
  </div>;
}
