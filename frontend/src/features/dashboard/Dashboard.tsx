import { useEffect, useState, type ComponentType } from "react";
import { AlertTriangle, Banknote, CreditCard, TrendingUp } from "lucide-react";
import { api } from "../../services/api";
import type { DashboardReport } from "../../types";
import { money, qty } from "../../utils/format";

export function Dashboard() {
  const [data, setData] = useState<DashboardReport | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.dashboard().then(setData).catch((err) => setError(err.message));
  }, []);

  if (error) return <section className="page"><div className="status status-error">{error}</div></section>;
  if (!data) return <section className="page"><div className="loading">Loading dashboard...</div></section>;

  return (
    <section className="page">
      <div className="page-title">
        <div>
          <h1>Dashboard</h1>
          <p>Today's sales, profit, expenses, and stock warnings.</p>
        </div>
      </div>
      <div className="metric-grid">
        <Metric icon={Banknote} label="Cash" value={money(data.today.cash_sales)} />
        <Metric icon={CreditCard} label="M-Pesa" value={money(data.today.mpesa_sales)} />
        <Metric icon={TrendingUp} label="Total Sales" value={money(data.today.total_sales)} />
        <Metric icon={ReceiptIcon} label="Transactions" value={String(data.today.transactions)} />
      </div>
      <div className="two-column">
        <div className="panel">
          <h2>Profit Today</h2>
          <dl className="summary-list">
            <div><dt>COGS</dt><dd>{money(data.today.cogs)}</dd></div>
            <div><dt>Gross Profit</dt><dd>{money(data.today.gross_profit)}</dd></div>
            <div><dt>Expenses</dt><dd>{money(data.today.expenses)}</dd></div>
            <div className="strong"><dt>Net Profit</dt><dd>{money(data.today.net_profit)}</dd></div>
          </dl>
        </div>
        <div className="panel">
          <h2>Low Stock</h2>
          {data.low_stock.length === 0 ? <p className="muted">No products below minimum stock.</p> : (
            <div className="list">
              {data.low_stock.map((item) => (
                <div className="list-row warning" key={item.product_id}>
                  <AlertTriangle size={18} />
                  <span>{item.product}</span>
                  <strong>{qty(item.current_stock, String(item.unit))}</strong>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      <div className="panel">
        <h2>Important Stock Levels</h2>
        <div className="responsive-table">
          <table>
            <thead><tr><th>Product</th><th>Current</th><th>Minimum</th><th>Status</th></tr></thead>
            <tbody>
              {data.inventory.map((item) => (
                <tr key={item.product_id}>
                  <td>{item.product}</td>
                  <td>{qty(item.current_stock, String(item.unit))}</td>
                  <td>{qty(item.minimum_stock, String(item.unit))}</td>
                  <td>{Number(item.current_stock) < Number(item.minimum_stock) ? "LOW STOCK" : "OK"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

function ReceiptIcon({ size = 18 }: { size?: number }) {
  return <span style={{ width: size, height: size, display: "inline-block" }}>#</span>;
}

function Metric({ icon: Icon, label, value }: { icon: ComponentType<{ size?: number }>; label: string; value: string }) {
  return <div className="metric"><Icon size={22} /><span>{label}</span><strong>{value}</strong></div>;
}
