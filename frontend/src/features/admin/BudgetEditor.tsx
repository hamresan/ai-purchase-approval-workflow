import { useState } from "react";
import type { HttpAdminApi } from "@/api/admin";
import type { AdminData } from "@/features/admin/types";

export function BudgetEditor({ api, data, reload }: { api: HttpAdminApi; data: AdminData; reload: () => Promise<void> }) {
  const [ownerType, setOwnerType] = useState<"USER" | "DEPARTMENT">("DEPARTMENT");
  const [ownerId, setOwnerId] = useState("");
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("USD");
  const add = async () => {
    if (!ownerId || !amount) return;
    await api.createBudget({ owner_type: ownerType, user_id: ownerType === "USER" ? ownerId : null,
      department_id: ownerType === "DEPARTMENT" ? ownerId : null, amount, currency, is_active: true });
    setAmount(""); await reload();
  };
  return <><div className="admin-resource-form">
    <select aria-label="Budget owner type" value={ownerType} onChange={e => { setOwnerType(e.target.value as "USER" | "DEPARTMENT"); setOwnerId(""); }}><option value="DEPARTMENT">Department</option><option value="USER">User</option></select>
    {ownerType === "DEPARTMENT" ? <select aria-label="Budget owner" value={ownerId} onChange={e => setOwnerId(e.target.value)}><option value="">Department</option>{data.departments.filter(x => x.is_active).map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select> : <select aria-label="Budget owner" value={ownerId} onChange={e => setOwnerId(e.target.value)}><option value="">User</option>{data.roles.map(x => <option key={x.user_id} value={x.user_id}>{x.user_id}</option>)}</select>}
    <input aria-label="Budget amount" type="number" min="0.01" step="0.01" placeholder="Limit" value={amount} onChange={e => setAmount(e.target.value)} />
    <input aria-label="Budget currency" maxLength={3} value={currency} onChange={e => setCurrency(e.target.value.toUpperCase())} />
    <button className="primary-button" onClick={() => void add()}>Add budget</button>
  </div><div className="admin-table-wrap"><table className="admin-table"><thead><tr><th>Owner</th><th>Currency</th><th>Limit</th><th>Status</th><th>Action</th></tr></thead>
    <tbody>{data.budgets.map(item => <tr key={item.id}><td>{item.owner_type === "USER" ? item.user_id : data.departments.find(x => x.id === item.department_id)?.name ?? item.department_id}</td><td>{item.currency}</td><td>{item.amount}</td><td>{item.is_active ? "Active" : "Inactive"}</td><td><button className="admin-link-button" onClick={() => void api.saveBudget({ ...item, is_active: !item.is_active }).then(reload)}>{item.is_active ? "Deactivate" : "Activate"}</button></td></tr>)}</tbody>
  </table></div></>;
}
