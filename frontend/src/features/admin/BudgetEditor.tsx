import { useState } from "react";
import type { Budget, HttpAdminApi } from "@/api/admin";
import type { AdminData } from "@/features/admin/types";

export function BudgetEditor({ api, data, reload }: { api: HttpAdminApi; data: AdminData; reload: () => Promise<void> }) {
  const [ownerType, setOwnerType] = useState<"USER" | "DEPARTMENT">("DEPARTMENT");
  const [ownerId, setOwnerId] = useState("");
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [editing, setEditing] = useState<Budget | null>(null);
  const add = async () => {
    if (!ownerId || !amount) return;
    await api.createBudget({ owner_type: ownerType, user_id: ownerType === "USER" ? ownerId : null,
      department_id: ownerType === "DEPARTMENT" ? ownerId : null, amount, currency, is_active: true });
    setAmount(""); await reload();
  };
  const saveEdit = async () => {
    if (!editing) return;
    await api.saveBudget(editing);
    setEditing(null);
    await reload();
  };
  const ownerValue = (item: Budget) => item.owner_type === "USER" ? item.user_id ?? "" : item.department_id ?? "";
  const changeEditOwner = (value: string) => {
    if (!editing) return;
    setEditing({ ...editing, user_id: editing.owner_type === "USER" ? value : null,
      department_id: editing.owner_type === "DEPARTMENT" ? value : null });
  };
  return <><div className="admin-resource-form">
    <select aria-label="Budget owner type" value={ownerType} onChange={e => { setOwnerType(e.target.value as "USER" | "DEPARTMENT"); setOwnerId(""); }}><option value="DEPARTMENT">Department</option><option value="USER">User</option></select>
    {ownerType === "DEPARTMENT" ? <select aria-label="Budget owner" value={ownerId} onChange={e => setOwnerId(e.target.value)}><option value="">Department</option>{data.departments.filter(x => x.is_active).map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select> : <select aria-label="Budget owner" value={ownerId} onChange={e => setOwnerId(e.target.value)}><option value="">User</option>{data.roles.map(x => <option key={x.user_id} value={x.user_id}>{x.user_id}</option>)}</select>}
    <input aria-label="Budget amount" type="number" min="0.01" step="0.01" placeholder="Limit" value={amount} onChange={e => setAmount(e.target.value)} />
    <input aria-label="Budget currency" maxLength={3} value={currency} onChange={e => setCurrency(e.target.value.toUpperCase())} />
    <button className="primary-button" onClick={() => void add()}>Add budget</button>
  </div><div className="admin-table-wrap"><table className="admin-table"><thead><tr><th>Owner</th><th>Currency</th><th>Limit</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>{data.budgets.map(item => <tr key={item.id}><td>{item.owner_type === "USER" ? item.user_id : data.departments.find(x => x.id === item.department_id)?.name ?? item.department_id}</td><td>{item.currency}</td><td>{item.amount}</td><td>{item.is_active ? "Active" : "Inactive"}</td><td><div className="admin-row-actions"><button className="admin-link-button" onClick={() => setEditing(item)}>Edit</button><button className="admin-link-button" onClick={() => void api.saveBudget({ ...item, is_active: !item.is_active }).then(reload)}>{item.is_active ? "Deactivate" : "Activate"}</button></div></td></tr>)}</tbody>
  </table></div>
  {editing && <div className="modal-backdrop" role="presentation"><div className="approval-dialog" role="dialog" aria-modal="true" aria-labelledby="edit-budget-title">
    <div className="dialog-heading"><div className="dialog-icon">✎</div><div><h2 id="edit-budget-title">Edit budget</h2><p>Update the trusted budget limit.</p></div><button className="dialog-close" aria-label="Close" onClick={() => setEditing(null)}>×</button></div>
    <div className="admin-resource-form admin-edit-form">
      <select aria-label="Edit budget owner" value={ownerValue(editing)} onChange={e => changeEditOwner(e.target.value)}>
        {editing.owner_type === "DEPARTMENT" ? data.departments.map(x => <option key={x.id} value={x.id}>{x.name}</option>) : data.roles.map(x => <option key={x.user_id} value={x.user_id}>{x.user_id}</option>)}
      </select>
      <input aria-label="Edit budget amount" type="number" min="0.01" step="0.01" value={editing.amount} onChange={e => setEditing({ ...editing, amount: e.target.value })} />
      <input aria-label="Edit budget currency" maxLength={3} value={editing.currency} onChange={e => setEditing({ ...editing, currency: e.target.value.toUpperCase() })} />
    </div>
    <div className="dialog-actions"><button className="secondary-button" onClick={() => setEditing(null)}>Cancel</button><button className="primary-button" onClick={() => void saveEdit()}>Save changes</button></div>
  </div></div>}
  </>;
}
