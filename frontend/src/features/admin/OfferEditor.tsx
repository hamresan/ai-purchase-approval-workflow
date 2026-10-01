import { useState } from "react";
import type { HttpAdminApi, Offer, Product, Vendor } from "@/api/admin";
import type { AdminData } from "@/features/admin/types";

export function OfferEditor({ api, data, reload }: { api: HttpAdminApi; data: AdminData; reload: () => Promise<void> }) {
  const [productId, setProductId] = useState("");
  const [vendorId, setVendorId] = useState("");
  const [price, setPrice] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [quantity, setQuantity] = useState("0");
  const [editing, setEditing] = useState<Offer | null>(null);
  const add = async () => {
    if (!productId || !vendorId || !price) return;
    await api.createOffer({ product_id: productId, vendor_id: vendorId, unit_price_amount: price,
      currency, available_quantity: Number(quantity), is_active: true });
    setPrice(""); setQuantity("0"); await reload();
  };
  const saveEdit = async () => {
    if (!editing) return;
    await api.saveOffer(editing);
    setEditing(null);
    await reload();
  };
  const name = (id: string, values: Array<Product | Vendor>) => values.find(item => item.id === id)?.name ?? id;
  return <><div className="admin-resource-form">
    <select aria-label="Product" value={productId} onChange={e => setProductId(e.target.value)}><option value="">Product</option>{data.products.filter(x => x.is_active).map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select>
    <select aria-label="Vendor" value={vendorId} onChange={e => setVendorId(e.target.value)}><option value="">Vendor</option>{data.vendors.filter(x => x.is_active).map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select>
    <input aria-label="Price" type="number" min="0.01" step="0.01" placeholder="Price" value={price} onChange={e => setPrice(e.target.value)} />
    <input aria-label="Currency" maxLength={3} value={currency} onChange={e => setCurrency(e.target.value.toUpperCase())} />
    <input aria-label="Available quantity" type="number" min="0" value={quantity} onChange={e => setQuantity(e.target.value)} />
    <button className="primary-button" onClick={() => void add()}>Add offer</button>
  </div><div className="admin-table-wrap"><table className="admin-table"><thead><tr><th>Product</th><th>Vendor</th><th>Price</th><th>Available</th><th>Actions</th></tr></thead>
    <tbody>{data.offers.map(item => <tr key={item.id}><td>{name(item.product_id, data.products)}</td><td>{name(item.vendor_id, data.vendors)}</td><td>{item.currency} {item.unit_price_amount}</td><td>{item.available_quantity}</td><td><div className="admin-row-actions"><button className="admin-link-button" onClick={() => setEditing(item)}>Edit</button><button className="admin-link-button" onClick={() => void api.saveOffer({ ...item, is_active: !item.is_active }).then(reload)}>{item.is_active ? "Deactivate" : "Activate"}</button></div></td></tr>)}</tbody>
  </table></div>
  {editing && <div className="modal-backdrop" role="presentation"><div className="approval-dialog" role="dialog" aria-modal="true" aria-labelledby="edit-offer-title">
    <div className="dialog-heading"><div className="dialog-icon">✎</div><div><h2 id="edit-offer-title">Edit trusted price</h2><p>Update trusted price and availability.</p></div><button className="dialog-close" aria-label="Close" onClick={() => setEditing(null)}>×</button></div>
    <div className="admin-resource-form admin-edit-form">
      <select aria-label="Edit offer product" value={editing.product_id} onChange={e => setEditing({ ...editing, product_id: e.target.value })}>{data.products.map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select>
      <select aria-label="Edit offer vendor" value={editing.vendor_id} onChange={e => setEditing({ ...editing, vendor_id: e.target.value })}>{data.vendors.map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select>
      <input aria-label="Edit offer price" type="number" min="0.01" step="0.01" value={editing.unit_price_amount} onChange={e => setEditing({ ...editing, unit_price_amount: e.target.value })} />
      <input aria-label="Edit offer currency" maxLength={3} value={editing.currency} onChange={e => setEditing({ ...editing, currency: e.target.value.toUpperCase() })} />
      <input aria-label="Edit offer available quantity" type="number" min="0" value={editing.available_quantity} onChange={e => setEditing({ ...editing, available_quantity: Number(e.target.value) })} />
    </div>
    <div className="dialog-actions"><button className="secondary-button" onClick={() => setEditing(null)}>Cancel</button><button className="primary-button" onClick={() => void saveEdit()}>Save changes</button></div>
  </div></div>}
  </>;
}
