import { useEffect, useMemo, useState } from "react";
import { Minus, Plus, Search, Trash2 } from "lucide-react";
import { Status } from "../../components/Status";
import { api, type CartItemPayload } from "../../services/api";
import type { PaymentMethod, Product, Unit } from "../../types";
import { money, paymentMethods, qty, units } from "../../utils/format";

interface CartLine {
  product: Product;
  mode: "quantity" | "amount";
  quantity: string;
  unit: Unit;
  amount: string;
}

export function POS() {
  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState("");
  const [cart, setCart] = useState<CartLine[]>([]);
  const [payment, setPayment] = useState<PaymentMethod>("Cash");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = () => api.products(true).then(setProducts).catch((err) => setError(err.message));
  useEffect(() => {
    void load();
  }, []);

  const visible = products.filter((p) => p.active && p.name.toLowerCase().includes(search.toLowerCase()));
  const subtotal = useMemo(() => cart.reduce((sum, line) => {
    if (line.mode === "amount") return sum + Number(line.amount || 0);
    return sum + Number(line.quantity || 0) * Number(line.product.selling_price || 0) * unitFactor(line.unit, line.product.unit);
  }, 0), [cart]);

  function add(product: Product) {
    setCart((items) => [...items, { product, mode: "quantity", quantity: "1", unit: product.unit, amount: "" }]);
  }

  function update(index: number, patch: Partial<CartLine>) {
    setCart((items) => items.map((item, i) => (i === index ? { ...item, ...patch } : item)));
  }

  async function completeSale() {
    setError("");
    setSuccess("");
    const items: CartItemPayload[] = cart.map((line) => ({
      product_id: line.product.id,
      mode: line.mode,
      unit: line.unit,
      quantity: line.mode === "quantity" ? line.quantity : undefined,
      amount: line.mode === "amount" ? line.amount : undefined,
    }));
    try {
      const sale = await api.createSale(items, payment);
      setSuccess(`Sale #${sale.id} completed: ${money(sale.total)}`);
      setCart([]);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sale failed");
    }
  }

  return (
    <section className="page pos-layout">
      <div className="pos-products">
        <div className="page-title">
          <div>
            <h1>POS</h1>
            <p>Search, add to cart, choose payment, and complete the sale.</p>
          </div>
        </div>
        <div className="search-box"><Search size={18} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search product" /></div>
        <div className="product-grid">
          {visible.map((product) => (
            <button className="product-tile" key={product.id} onClick={() => add(product)}>
              <strong>{product.name}</strong>
              <span>{money(product.selling_price)} / {product.unit}</span>
              <small>{qty(product.current_stock, product.unit)}</small>
            </button>
          ))}
        </div>
      </div>
      <aside className="cart-panel">
        <h2>Cart</h2>
        <Status error={error} success={success} />
        {cart.length === 0 ? <p className="muted">No items added.</p> : cart.map((line, index) => (
          <div className="cart-line" key={`${line.product.id}-${index}`}>
            <div className="cart-line-head">
              <strong>{line.product.name}</strong>
              <button className="icon-button" onClick={() => setCart((items) => items.filter((_, i) => i !== index))}><Trash2 size={16} /></button>
            </div>
            <div className="segmented">
              <button className={line.mode === "quantity" ? "selected" : ""} onClick={() => update(index, { mode: "quantity" })}>Quantity</button>
              <button className={line.mode === "amount" ? "selected" : ""} onClick={() => update(index, { mode: "amount", unit: "Millilitre" })}>Amount</button>
            </div>
            {line.mode === "quantity" ? (
              <div className="inline-fields">
                <button className="icon-button" onClick={() => update(index, { quantity: String(Math.max(0.001, Number(line.quantity) - 1)) })}><Minus size={16} /></button>
                <input type="number" min="0" step="0.001" value={line.quantity} onChange={(e) => update(index, { quantity: e.target.value })} />
                <button className="icon-button" onClick={() => update(index, { quantity: String(Number(line.quantity || 0) + 1) })}><Plus size={16} /></button>
                <select value={line.unit} onChange={(e) => update(index, { unit: e.target.value as Unit })}>
                  {units.map((unit) => <option key={unit}>{unit}</option>)}
                </select>
              </div>
            ) : (
              <div className="inline-fields">
                <input type="number" min="0" step="0.01" value={line.amount} onChange={(e) => update(index, { amount: e.target.value })} placeholder="KSh amount" />
                <select value={line.unit} onChange={(e) => update(index, { unit: e.target.value as Unit })}>
                  {units.map((unit) => <option key={unit}>{unit}</option>)}
                </select>
              </div>
            )}
          </div>
        ))}
        <div className="checkout">
          <div><span>Subtotal</span><strong>{money(subtotal)}</strong></div>
          <label>Payment</label>
          <div className="segmented">
            {paymentMethods.map((method) => <button key={method} className={payment === method ? "selected" : ""} onClick={() => setPayment(method)}>{method}</button>)}
          </div>
          <button className="primary wide" disabled={cart.length === 0} onClick={completeSale}>Complete Sale</button>
        </div>
      </aside>
    </section>
  );
}

function unitFactor(from: Unit, to: Unit) {
  if (from === to) return 1;
  if (from === "Millilitre" && to === "Litre") return 0.001;
  if (from === "Gram" && to === "Kilogram") return 0.001;
  if (from === "Litre" && to === "Millilitre") return 1000;
  if (from === "Kilogram" && to === "Gram") return 1000;
  return 1;
}
