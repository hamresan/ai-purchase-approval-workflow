import { useState } from "react";
import { runAdminMutation } from "@/features/admin/mutation";

export function NamedResourceEditor<T extends { id: string; name: string; is_active: boolean }>({
  kind, items, create, save, reload, onError,
}: {
  kind: string;
  items: T[];
  create: (name: string) => Promise<unknown>;
  save: (item: T) => Promise<unknown>;
  reload: () => Promise<void>;
  onError: (message: string) => void;
}) {
  const [name, setName] = useState("");
  const [editing, setEditing] = useState<T | null>(null);
  const [editName, setEditName] = useState("");

  const submit = async () => {
    if (!name.trim()) return;
    const succeeded = await runAdminMutation(async () => {
      await create(name.trim());
      await reload();
    }, onError);
    if (succeeded) setName("");
  };
  const startEdit = (item: T) => {
    setEditing(item);
    setEditName(item.name);
  };
  const submitEdit = async () => {
    if (!editing || !editName.trim()) return;
    const succeeded = await runAdminMutation(async () => {
      await save({ ...editing, name: editName.trim() });
      await reload();
    }, onError);
    if (succeeded) setEditing(null);
  };

  return <>
    <div className="admin-inline-form">
      <input aria-label={`New ${kind}`} placeholder={`New ${kind.toLowerCase()} name`} value={name}
        onChange={event => setName(event.target.value)} />
      <button className="primary-button" onClick={() => void submit()}>Add</button>
    </div>
    <div className="admin-table-wrap"><table className="admin-table">
      <thead><tr><th>{kind}</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody>{items.map(item => <tr key={item.id}><td>{item.name}</td>
        <td>{item.is_active ? "Active" : "Inactive"}</td>
        <td><div className="admin-row-actions"><button className="admin-link-button" onClick={() => startEdit(item)}>Edit</button>
          <button className="admin-link-button"
            onClick={() => void runAdminMutation(async () => {
              await save({ ...item, is_active: !item.is_active });
              await reload();
            }, onError)}>
            {item.is_active ? "Deactivate" : "Activate"}
          </button></div></td></tr>)}</tbody>
    </table></div>
    {editing && <div className="modal-backdrop" role="presentation">
      <div className="approval-dialog" role="dialog" aria-modal="true" aria-labelledby="edit-resource-title">
        <div className="dialog-heading"><div className="dialog-icon">✎</div><div>
          <h2 id="edit-resource-title">Edit {kind}</h2><p>Update the trusted {kind.toLowerCase()} name.</p>
        </div><button className="dialog-close" aria-label="Close" onClick={() => setEditing(null)}>×</button></div>
        <label className="dialog-field">Name
          <input aria-label={`Edit ${kind} name`} value={editName} onChange={event => setEditName(event.target.value)} />
        </label>
        <div className="dialog-actions"><button className="secondary-button" onClick={() => setEditing(null)}>Cancel</button>
          <button className="primary-button" onClick={() => void submitEdit()}>Save changes</button></div>
      </div>
    </div>}
  </>;
}
