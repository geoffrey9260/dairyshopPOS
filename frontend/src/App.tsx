import { useEffect, useState, type ComponentType } from "react";
import {
  BarChart3,
  Boxes,
  Cog,
  Home,
  Milk,
  ReceiptText,
  ShoppingCart,
} from "lucide-react";
import { Dashboard } from "./features/dashboard/Dashboard";
import { Expenses } from "./features/expenses/Expenses";
import { Inventory } from "./features/inventory/Inventory";
import { POS } from "./features/pos/POS";
import { Products } from "./features/products/Products";
import { Reports } from "./features/reports/Reports";
import { SettingsPage } from "./features/settings/SettingsPage";
import { api } from "./services/api";

type Page = "dashboard" | "pos" | "products" | "inventory" | "expenses" | "reports" | "settings";

const navItems: Array<{ id: Page; label: string; icon: ComponentType<{ size?: number }> }> = [
  { id: "dashboard", label: "Dashboard", icon: Home },
  { id: "pos", label: "POS", icon: ShoppingCart },
  { id: "products", label: "Products", icon: Milk },
  { id: "inventory", label: "Inventory", icon: Boxes },
  { id: "expenses", label: "Expenses", icon: ReceiptText },
  { id: "reports", label: "Reports", icon: BarChart3 },
  { id: "settings", label: "Settings", icon: Cog },
];

export default function App() {
  const [activePage, setActivePage] = useState<Page>("dashboard");
  const [shopName, setShopName] = useState("Dairy Shop");

  useEffect(() => {
    api.settings()
      .then((settings) => setShopName(settings.shop_name ?? "Dairy Shop"))
      .catch(() => {
        setShopName("Dairy Shop");
      });
  }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Milk size={34} />
          <div>
            <strong>{shopName}</strong>
            <span>Point of sale</span>
          </div>
        </div>
        <nav aria-label="Main navigation">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button
              className={activePage === id ? "active" : ""}
              key={id}
              onClick={() => setActivePage(id)}
              type="button"
            >
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </aside>
      <main className="content">
        {activePage === "dashboard" && <Dashboard />}
        {activePage === "pos" && <POS />}
        {activePage === "products" && <Products />}
        {activePage === "inventory" && <Inventory />}
        {activePage === "expenses" && <Expenses />}
        {activePage === "reports" && <Reports />}
        {activePage === "settings" && <SettingsPage onShopName={setShopName} />}
      </main>
    </div>
  );
}
