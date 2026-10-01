import { useState } from "react";

export function NamedResourceEditor<T extends { id: string; name: string; is_active: boolean }>({
  kind, items, create, save, reload,
}: {
  kind: string;
  items: T[];
  create: (name: string) => Promise<unknown>;
  save: (item: T) => Promise<unknown>;
  reload: () => Promise<void>;
}) {
  const [name, setName] = useState("");
  const submit = async () => {
    if (!name.trim()) return;
    await create(name.trim());
    setName("");
    await reload();
  };
  return <>
    <div className="admin-inline-form">
      <input aria-label={`New ${kind}`} placeholder={`New ${kind.toLowerCase()} name`} value={name}
        onChange={event => setName(event.target.value)} />
      <button className="primary-button" onClick={() => void submit()}>Add</button>
    </div>
    <div className="admin-table-wrap"><table className="admin-table">
      <thead><tr><th>{kind}</th><th>Status</th><th>Action</th></tr></thead>
      <tbody>{items.map(item => <tr key={item.id}><td>{item.name}</td>
        <td>{item.is_active ? "Active" : "Inactive"}</td>
        <td><button className="admin-link-button"
          onClick={() => void save({ ...item, is_active: !item.is_active }).then(reload)}>
          {item.is_active ? "Deactivate" : "Activate"}
        </button></td></tr>)}</tbody>
    </table></div>
  </>;
}
