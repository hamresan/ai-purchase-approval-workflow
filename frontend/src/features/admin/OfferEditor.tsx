import { useState } from "react";
import type { HttpAdminApi, Product, Vendor } from "@/api/admin";
import type { AdminData } from "@/features/admin/types";

export function OfferEditor({ api, data, reload }: { api: HttpAdminApi; data: AdminData; reload: () => Promise<void> }) {
  const [productId, setProductId] = useState("");
  const [vendorId, setVendorId] = useState("");
  const [price, setPrice] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [quantity, setQuantity] = useState("0");
  const add = async () => {
    if (!productId || !vendorId || !price) return;
    await api.createOffer({ product_id: productId, vendor_id: vendorId, unit_price_amount: price,
      currency, available_quantity: Number(quantity), is_active: true });
    setPrice(""); setQuantity("0"); await reload();
  };
  const name = (id: string, values: Array<Product | Vendor>) => values.find(item => item.id === id)?.name ?? id;
  return <><div className="admin-resource-form">
    <select aria-label="Product" value={productId} onChange={e => setProductId(e.target.value)}><option value="">Product</option>{data.products.filter(x => x.is_active).map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select>
    <select aria-label="Vendor" value={vendorId} onChange={e => setVendorId(e.target.value)}><option value="">Vendor</option>{data.vendors.filter(x => x.is_active).map(x => <option key={x.id} value={x.id}>{x.name}</option>)}</select>
    <input aria-label="Price" type="number" min="0.01" step="0.01" placeholder="Price" value={price} onChange={e => setPrice(e.target.value)} />
    <input aria-label="Currency" maxLength={3} value={currency} onChange={e => setCurrency(e.target.value.toUpperCase())} />
    <input aria-label="Available quantity" type="number" min="0" value={quantity} onChange={e => setQuantity(e.target.value)} />
    <button className="primary-button" onClick={() => void add()}>Add offer</button>
  </div><div className="admin-table-wrap"><table className="admin-table"><thead><tr><th>Product</th><th>Vendor</th><th>Price</th><th>Available</th><th>Action</th></tr></thead>
    <tbody>{data.offers.map(item => <tr key={item.id}><td>{name(item.product_id, data.products)}</td><td>{name(item.vendor_id, data.vendors)}</td><td>{item.currency} {item.unit_price_amount}</td><td>{item.available_quantity}</td><td><button className="admin-link-button" onClick={() => void api.saveOffer({ ...item, is_active: !item.is_active }).then(reload)}>{item.is_active ? "Deactivate" : "Activate"}</button></td></tr>)}</tbody>
  </table></div></>;
}
