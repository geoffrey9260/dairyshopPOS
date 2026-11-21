import { FormEvent, useEffect, useState } from "react";
import { ClipboardCheck, PackagePlus } from "lucide-react";
import { Status } from "../../components/Status";
import { api } from "../../services/api";
import type { Product, StockMovement, Unit } from "../../types";
import { money, qty, units } from "../../utils/format";

export function Inventory() {
  const [products, setProducts] = useState<Product[]>([]);
  const [movements, setMovements] = useState<StockMovement[]>([]);
  const [receive, setReceive] = useState({ product_id: 0, quantity: "", unit: "Piece" as Unit, unit_cost: "", notes: "" });
  const [count, setCount] = useState({ product_id: 0, counted_quantity: "", unit: "Piece" as Unit, reason: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = () => Promise.all([api.products(false), api.movements()]).then(([products, movements]) => {
    setProducts(products);
    setMovements(movements);
    const first = products[0];
    if (first && receive.product_id === 0) {
      setReceive((value) => ({ ...value, product_id: first.id, unit: first.unit }));
      setCount((value) => ({ ...value, product_id: first.id, unit: first.unit }));
    }
  }).catch((err) => setError(err.message));
  useEffect(() => {
    void load();
  }, []);

  async function submitReceive(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await api.receiveStock({ items: [{ product_id: receive.product_id, quantity: receive.quantity, unit: receive.unit, unit_cost: receive.unit_cost }], notes: receive.notes });
      setSuccess("Stock received");
      setReceive({ ...receive, quantity: "", unit_cost: "", notes: "" });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to receive stock");
    }
  }

  async function submitCount(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await api.stockCount(count);
      setSuccess("Stock count recorded with adjustment trail");
      setCount({ ...count, counted_quantity: "", reason: "" });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to record stock count");
    }
  }

  return (
    <section className="page">
      <div className="page-title"><div><h1>Inventory</h1><p>Receive stock, count physical stock, and review stock movements.</p></div></div>
      <Status error={error} success={success} />
      <div className="two-column">
        <form className="panel form-grid" onSubmit={submitReceive}>
          <h2><PackagePlus size={18} /> Receive Stock</h2>
          <ProductSelect products={products} value={receive.product_id} onChange={(product) => setReceive({ ...receive, product_id: product.id, unit: product.unit })} />
          <label>Quantity<input required type="number" step="0.001" min="0" value={receive.quantity} onChange={(e) => setReceive({ ...receive, quantity: e.target.value })} /></label>
          <label>Unit<select value={receive.unit} onChange={(e) => setReceive({ ...receive, unit: e.target.value as Unit })}>{units.map((unit) => <option key={unit}>{unit}</option>)}</select></label>
          <label>Buying cost per unit<input required type="number" step="0.0001" min="0" value={receive.unit_cost} onChange={(e) => setReceive({ ...receive, unit_cost: e.target.value })} /></label>
          <label>Notes<textarea value={receive.notes} onChange={(e) => setReceive({ ...receive, notes: e.target.value })} /></label>
          <button className="primary">Receive</button>
        </form>
        <form className="panel form-grid" onSubmit={submitCount}>
          <h2><ClipboardCheck size={18} /> Stock Count</h2>
          <ProductSelect products={products} value={count.product_id} onChange={(product) => setCount({ ...count, product_id: product.id, unit: product.unit })} />
          <label>Physical quantity<input required type="number" step="0.001" min="0" value={count.counted_quantity} onChange={(e) => setCount({ ...count, counted_quantity: e.target.value })} /></label>
          <label>Unit<select value={count.unit} onChange={(e) => setCount({ ...count, unit: e.target.value as Unit })}>{units.map((unit) => <option key={unit}>{unit}</option>)}</select></label>
          <label>Reason<input required value={count.reason} onChange={(e) => setCount({ ...count, reason: e.target.value })} placeholder="Spillage, spoilage, counting error..." /></label>
          <button className="primary">Record Count</button>
        </form>
      </div>
      <div className="panel">
        <h2>Current Stock</h2>
        <div className="inventory-cards">{products.map((product) => <div className="stock-card" key={product.id}><strong>{product.name}</strong><span>{qty(product.current_stock, product.unit)}</span><small>Avg cost {money(product.average_cost)}</small></div>)}</div>
      </div>
      <div className="panel">
        <h2>Stock Movements</h2>
        <div className="responsive-table"><table><thead><tr><th>Date</th><th>Product</th><th>Type</th><th>Quantity</th><th>Before</th><th>After</th><th>Reason</th></tr></thead><tbody>
          {movements.map((movement) => {
            const product = products.find((p) => p.id === movement.product_id);
            return <tr key={movement.id}><td>{new Date(movement.created_at).toLocaleString()}</td><td>{product?.name ?? movement.product_id}</td><td>{movement.movement_type}</td><td>{qty(movement.quantity, movement.unit)}</td><td>{qty(movement.previous_quantity, movement.unit)}</td><td>{qty(movement.new_quantity, movement.unit)}</td><td>{movement.reason}</td></tr>;
          })}
        </tbody></table></div>
      </div>
    </section>
  );
}

function ProductSelect({ products, value, onChange }: { products: Product[]; value: number; onChange: (product: Product) => void }) {
  return <label>Product<select value={value} onChange={(e) => { const product = products.find((p) => p.id === Number(e.target.value)); if (product) onChange(product); }}>{products.map((product) => <option key={product.id} value={product.id}>{product.name}</option>)}</select></label>;
}
