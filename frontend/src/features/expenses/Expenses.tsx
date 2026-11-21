import { FormEvent, useEffect, useState } from "react";
import { Status } from "../../components/Status";
import { api } from "../../services/api";
import type { Expense, ExpenseCategory } from "../../types";
import { money, todayIso } from "../../utils/format";

export function Expenses() {
  const [categories, setCategories] = useState<ExpenseCategory[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [form, setForm] = useState({ category_id: 0, amount: "", description: "", expense_date: todayIso(), notes: "" });
  const [newCategory, setNewCategory] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = () => Promise.all([api.expenseCategories(), api.expenses()]).then(([categories, expenses]) => {
    setCategories(categories);
    setExpenses(expenses);
    if (categories[0] && form.category_id === 0) setForm((value) => ({ ...value, category_id: categories[0].id }));
  }).catch((err) => setError(err.message));
  useEffect(() => {
    void load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await api.createExpense(form);
      setSuccess("Expense recorded");
      setForm({ ...form, amount: "", description: "", notes: "" });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to record expense");
    }
  }

  async function addCategory() {
    if (!newCategory.trim()) return;
    const category = await api.createExpenseCategory(newCategory.trim());
    setCategories((items) => [...items, category]);
    setForm((value) => ({ ...value, category_id: category.id }));
    setNewCategory("");
  }

  return (
    <section className="page">
      <div className="page-title"><div><h1>Expenses</h1><p>Record operating expenses separately from stock purchases.</p></div></div>
      <Status error={error} success={success} />
      <div className="two-column">
        <form className="panel form-grid" onSubmit={submit}>
          <h2>Add Expense</h2>
          <label>Category<select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: Number(e.target.value) })}>{categories.map((c) => <option value={c.id} key={c.id}>{c.name}</option>)}</select></label>
          <div className="inline-fields"><input value={newCategory} onChange={(e) => setNewCategory(e.target.value)} placeholder="New category" /><button type="button" onClick={addCategory}>Add</button></div>
          <label>Amount<input required type="number" step="0.01" min="0" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} /></label>
          <label>Description<input required value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
          <label>Date<input required type="date" value={form.expense_date} onChange={(e) => setForm({ ...form, expense_date: e.target.value })} /></label>
          <label>Notes<textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></label>
          <button className="primary">Save Expense</button>
        </form>
        <div className="panel">
          <h2>Expense List</h2>
          <div className="responsive-table"><table><thead><tr><th>Date</th><th>Category</th><th>Description</th><th>Amount</th></tr></thead><tbody>
            {expenses.map((expense) => <tr key={expense.id}><td>{expense.expense_date}</td><td>{expense.category_name}</td><td>{expense.description}</td><td>{money(expense.amount)}</td></tr>)}
          </tbody></table></div>
        </div>
      </div>
    </section>
  );
}
