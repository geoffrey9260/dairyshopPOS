import { FormEvent, useEffect, useState } from "react";
import { Power, PowerOff, Save } from "lucide-react";
import { Status } from "../../components/Status";
import { api, type ProductPayload } from "../../services/api";
import type { Category, Product, Unit } from "../../types";
import { money, qty, units } from "../../utils/format";

const blank: ProductPayload = {
  name: "",
  category_id: 0,
  unit: "Piece",
  selling_price: "",
  buying_price: "",
  minimum_stock: "0",
  current_stock: "0",
  average_cost: "",
};

export function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [form, setForm] = useState<ProductPayload>(blank);
  const [editing, setEditing] = useState<Product | null>(null);
  const [newCategory, setNewCategory] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = () => {
    Promise.all([api.products(false), api.categories()]).then(([products, categories]) => {
      setProducts(products);
      setCategories(categories);
      if (categories[0] && form.category_id === 0) setForm((value) => ({ ...value, category_id: categories[0].id }));
    }).catch((err) => setError(err.message));
  };
  useEffect(load, []);

  function edit(product: Product) {
    setEditing(product);
    setForm({
      name: product.name,
      category_id: product.category_id,
      unit: product.unit,
      selling_price: product.selling_price,
      buying_price: product.buying_price ?? "",
      minimum_stock: product.minimum_stock,
      current_stock: product.current_stock,
      average_cost: product.average_cost,
    });
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setSuccess("");
    try {
      const payload = { ...form, buying_price: form.buying_price || null, average_cost: form.average_cost || null };
      if (editing) {
        await api.updateProduct(editing.id, payload);
        setSuccess("Product updated");
      } else {
        await api.createProduct(payload);
        setSuccess("Product added");
      }
      setEditing(null);
      setForm({ ...blank, category_id: categories[0]?.id ?? 0 });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save product");
    }
  }

  async function addCategory() {
    if (!newCategory.trim()) return;
    const category = await api.createCategory(newCategory.trim());
    setCategories((items) => [...items, category]);
    setForm((value) => ({ ...value, category_id: category.id }));
    setNewCategory("");
  }

  async function toggle(product: Product) {
    product.active ? await api.deactivateProduct(product.id) : await api.reactivateProduct(product.id);
    load();
  }

  return (
    <section className="page">
      <div className="page-title"><div><h1>Products</h1><p>Add, edit, deactivate, and reactivate shop products.</p></div></div>
      <Status error={error} success={success} />
      <div className="two-column">
        <form className="panel form-grid" onSubmit={submit}>
          <h2>{editing ? "Edit Product" : "Add Product"}</h2>
          <label>Name<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
          <label>Category<select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: Number(e.target.value) })}>{categories.map((c) => <option value={c.id} key={c.id}>{c.name}</option>)}</select></label>
          <div className="inline-fields">
            <input value={newCategory} onChange={(e) => setNewCategory(e.target.value)} placeholder="New category" />
            <button type="button" onClick={addCategory}>Add</button>
          </div>
          <label>Unit<select value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value as Unit })}>{units.map((unit) => <option key={unit}>{unit}</option>)}</select></label>
          <label>Selling price<input required type="number" step="0.01" min="0" value={form.selling_price} onChange={(e) => setForm({ ...form, selling_price: e.target.value })} /></label>
          <label>Buying price<input type="number" step="0.0001" min="0" value={form.buying_price ?? ""} onChange={(e) => setForm({ ...form, buying_price: e.target.value })} /></label>
          <label>Minimum stock<input required type="number" step="0.001" min="0" value={form.minimum_stock} onChange={(e) => setForm({ ...form, minimum_stock: e.target.value })} /></label>
          {!editing && <label>Opening stock<input type="number" step="0.001" min="0" value={form.current_stock} onChange={(e) => setForm({ ...form, current_stock: e.target.value })} /></label>}
          <button className="primary" type="submit"><Save size={18} />Save Product</button>
        </form>
        <div className="panel">
          <h2>Product List</h2>
          <div className="responsive-table">
            <table>
              <thead><tr><th>Product</th><th>Category</th><th>Unit</th><th>Price</th><th>Stock</th><th>Status</th><th></th></tr></thead>
              <tbody>
                {products.map((product) => (
                  <tr key={product.id}>
                    <td><button className="text-button" onClick={() => edit(product)}>{product.name}</button></td>
                    <td>{product.category_name}</td>
                    <td>{product.unit}</td>
                    <td>{money(product.selling_price)}</td>
                    <td>{qty(product.current_stock, product.unit)}</td>
                    <td>{product.active ? "Active" : "Inactive"}</td>
                    <td><button className="icon-button" onClick={() => toggle(product)}>{product.active ? <PowerOff size={16} /> : <Power size={16} />}</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}
