import { useState } from "react";
import type { HttpAdminApi, RoleAssignment } from "@/api/admin";

const AVAILABLE_ROLES = ["requester", "approver", "admin"] as const;

interface Props {
  api: HttpAdminApi;
  assignments: RoleAssignment[];
  onChanged: (assignments: RoleAssignment[]) => void;
}

export function RoleManagement({ api, assignments, onChanged }: Props) {
  const [savingUserId, setSavingUserId] = useState<string | null>(null);
  const [error, setError] = useState("");

  async function toggleRole(assignment: RoleAssignment, role: string) {
    const selected = new Set(assignment.roles);
    if (selected.has(role)) {
      selected.delete(role);
    } else {
      selected.add(role);
    }
    if (selected.size === 0) {
      setError("Each user must keep at least one application role.");
      return;
    }
    setError("");
    setSavingUserId(assignment.user_id);
    try {
      const updated = await api.replaceRoles(assignment.user_id, [...selected]);
      onChanged(assignments.map(item => item.user_id === updated.user_id ? updated : item));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to update user roles.");
    } finally {
      setSavingUserId(null);
    }
  }

  return <>
    {error && <div className="admin-error" role="alert">{error}</div>}
    <div className="admin-table-wrap"><table className="admin-table">
      <thead><tr><th>User ID</th><th>Application roles</th></tr></thead>
      <tbody>{assignments.map(assignment => <tr key={assignment.user_id}>
        <td>{assignment.user_id}</td>
        <td><div className="role-options">{AVAILABLE_ROLES.map(role =>
          <label key={role}><input type="checkbox" checked={assignment.roles.includes(role)} disabled={savingUserId === assignment.user_id} onChange={() => void toggleRole(assignment, role)} /> {role[0].toUpperCase() + role.slice(1)}</label>
        )}</div></td>
      </tr>)}</tbody>
    </table></div>
  </>;
}
