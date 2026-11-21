import { useEffect, useState } from "react";
import { api } from "../../services/api";
import type { Product } from "../../types";
import { money, qty, todayIso } from "../../utils/format";

interface ProductRow {
  product_id: number;
  product: string;
  quantity_sold: string;
  revenue: string;
  cost: string;
  gross_profit: string;
}

interface Summary {
  total_sales: string;
  cash_sales: string;
  mpesa_sales: string;
  transactions: number;
  cogs: string;
  gross_profit: string;
  expenses: string;
  net_profit: string;
}

interface ExpenseReport {
  rows: Array<{ category: string; amount: string; date: string; description: string }>;
  total_expenses: string;
}

interface MilkReport {
  quantity_sold: string;
  revenue: string;
  cost: string;
  gross_profit: string;
  rows: ProductRow[];
}

type Period = "daily" | "weekly" | "monthly";

export function Reports() {
  const [day, setDay] = useState(todayIso());
  const [period, setPeriod] = useState<Period>("daily");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [products, setProducts] = useState<ProductRow[]>([]);
  const [milk, setMilk] = useState<MilkReport | null>(null);
  const [milkProductId, setMilkProductId] = useState(0);
  const [inventory, setInventory] = useState<Array<Record<string, string | number>>>([]);
  const [expenses, setExpenses] = useState<ExpenseReport | null>(null);
  const [shopProducts, setShopProducts] = useState<Product[]>([]);
  const [error, setError] = useState("");

  const range = reportRange(day, period);
  const litreProducts = shopProducts.filter((product) => product.unit === "Litre");

  const load = () => Promise.all([
    summaryRequest(period, day),
    api.productReport(range.start, range.end),
    api.milkReport(range.start, range.end, milkProductId || undefined),
    api.inventoryReport(),
    api.expenseReport(range.start, range.end),
    api.products(false),
  ])
    .then(([summary, products, milk, inventory, expenses, shopProducts]) => {
      setSummary(summary as Summary);
      setProducts(products as ProductRow[]);
      setMilk(milk as MilkReport);
      setInventory(inventory);
      setExpenses(expenses as ExpenseReport);
      setShopProducts(shopProducts as Product[]);
    })
    .catch((err) => setError(err.message));
  useEffect(() => {
    void load();
  }, [day, period, milkProductId]);

  return (
    <section className="page">
      <div className="page-title">
        <div><h1>Reports</h1><p>Closing summaries, product performance, milk, expenses, and inventory status.</p></div>
        <div className="report-controls">
          <label>Period<select value={period} onChange={(e) => setPeriod(e.target.value as Period)}><option value="daily">Daily</option><option value="weekly">Weekly</option><option value="monthly">Monthly</option></select></label>
          <label className="date-filter">Date<input type="date" value={day} onChange={(e) => setDay(e.target.value)} /></label>
        </div>
      </div>
      {error && <div className="status status-error">{error}</div>}
      {summary && (
        <div className="panel">
          <h2>{periodLabel(period)} Closing</h2>
          <dl className="summary-list closing">
            <div><dt>Cash</dt><dd>{money(summary.cash_sales)}</dd></div>
            <div><dt>M-Pesa</dt><dd>{money(summary.mpesa_sales)}</dd></div>
            <div><dt>Total</dt><dd>{money(summary.total_sales)}</dd></div>
            <div><dt>COGS</dt><dd>{money(summary.cogs)}</dd></div>
            <div><dt>Gross Profit</dt><dd>{money(summary.gross_profit)}</dd></div>
            <div><dt>Expenses</dt><dd>{money(summary.expenses)}</dd></div>
            <div className="strong"><dt>Net Profit</dt><dd>{money(summary.net_profit)}</dd></div>
            <div><dt>Transactions</dt><dd>{summary.transactions}</dd></div>
          </dl>
        </div>
      )}
      <div className="three-column">
        <div className="panel">
          <h2>Product Report</h2>
          <div className="responsive-table"><table><thead><tr><th>Product</th><th>Sold</th><th>Revenue</th><th>Cost</th><th>Gross Profit</th></tr></thead><tbody>
            {products.map((row) => <tr key={row.product_id}><td>{row.product}</td><td>{qty(row.quantity_sold)}</td><td>{money(row.revenue)}</td><td>{money(row.cost)}</td><td>{money(row.gross_profit)}</td></tr>)}
          </tbody></table></div>
        </div>
        <div className="panel">
          <div className="panel-heading">
            <h2>Milk Report</h2>
            <select value={milkProductId} onChange={(e) => setMilkProductId(Number(e.target.value))}>
              <option value={0}>All litre products</option>
              {litreProducts.map((product) => <option value={product.id} key={product.id}>{product.name}</option>)}
            </select>
          </div>
          {milk && <dl className="summary-list">
            <div><dt>Quantity</dt><dd>{qty(milk.quantity_sold, "Litre")}</dd></div>
            <div><dt>Revenue</dt><dd>{money(milk.revenue)}</dd></div>
            <div><dt>Cost</dt><dd>{money(milk.cost)}</dd></div>
            <div className="strong"><dt>Gross Profit</dt><dd>{money(milk.gross_profit)}</dd></div>
          </dl>}
        </div>
        <div className="panel">
          <h2>Inventory Report</h2>
          <div className="responsive-table"><table><thead><tr><th>Product</th><th>Stock</th><th>Minimum</th><th>Status</th></tr></thead><tbody>
            {inventory.map((row) => <tr key={row.product_id}><td>{row.product}</td><td>{qty(row.current_stock, String(row.unit))}</td><td>{qty(row.minimum_stock, String(row.unit))}</td><td>{row.status}</td></tr>)}
          </tbody></table></div>
        </div>
      </div>
      <div className="panel">
        <h2>Expense Report</h2>
        {expenses && <p className="report-total">Total expenses: <strong>{money(expenses.total_expenses)}</strong></p>}
        <div className="responsive-table"><table><thead><tr><th>Date</th><th>Category</th><th>Description</th><th>Amount</th></tr></thead><tbody>
          {expenses?.rows.map((row, index) => <tr key={`${row.date}-${row.category}-${index}`}><td>{row.date}</td><td>{row.category}</td><td>{row.description}</td><td>{money(row.amount)}</td></tr>)}
        </tbody></table></div>
      </div>
    </section>
  );
}

function summaryRequest(period: Period, day: string) {
  if (period === "weekly") return api.weeklyReport(reportRange(day, period).start);
  if (period === "monthly") {
    const selected = new Date(`${day}T00:00:00`);
    return api.monthlyReport(selected.getFullYear(), selected.getMonth() + 1);
  }
  return api.dailyReport(day);
}

function reportRange(day: string, period: Period) {
  const selected = new Date(`${day}T00:00:00`);
  if (period === "weekly") {
    const start = new Date(selected);
    start.setDate(selected.getDate() - ((selected.getDay() + 6) % 7));
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    return { start: toIso(start), end: toIso(end) };
  }
  if (period === "monthly") {
    const start = new Date(selected.getFullYear(), selected.getMonth(), 1);
    const end = new Date(selected.getFullYear(), selected.getMonth() + 1, 0);
    return { start: toIso(start), end: toIso(end) };
  }
  return { start: day, end: day };
}

function toIso(date: Date) {
  return date.toISOString().slice(0, 10);
}

function periodLabel(period: Period) {
  return period[0].toUpperCase() + period.slice(1);
}
