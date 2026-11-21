export type Unit = "Piece" | "Millilitre" | "Litre" | "Gram" | "Kilogram" | "Pack" | "Bottle" | "Box";
export type PaymentMethod = "Cash" | "M-Pesa";

export interface Category {
  id: number;
  name: string;
}

export interface Product {
  id: number;
  name: string;
  category_id: number;
  category_name: string;
  unit: Unit;
  selling_price: string;
  buying_price: string | null;
  minimum_stock: string;
  current_stock: string;
  average_cost: string;
  active: boolean;
  stock_status: string;
}

export interface SaleItem {
  id: number;
  product_id: number;
  product_name: string;
  quantity: string;
  unit: Unit;
  entered_quantity: string;
  entered_unit: Unit;
  unit_price: string;
  line_total: string;
  unit_cost: string;
  cogs: string;
  gross_profit: string;
}

export interface Sale {
  id: number;
  subtotal: string;
  total: string;
  payment_method: PaymentMethod;
  cogs: string;
  gross_profit: string;
  created_at: string;
  items: SaleItem[];
}

export interface ExpenseCategory {
  id: number;
  name: string;
}

export interface Expense {
  id: number;
  category_id: number;
  category_name: string;
  amount: string;
  description: string;
  expense_date: string;
  notes: string | null;
  created_at: string;
}

export interface SummaryReport {
  total_sales: string;
  cash_sales: string;
  mpesa_sales: string;
  transactions: number;
  cogs: string;
  gross_profit: string;
  expenses: string;
  net_profit: string;
}

export interface DashboardReport {
  today: SummaryReport;
  low_stock: Array<Record<string, string | number>>;
  inventory: Array<Record<string, string | number>>;
}

export interface StockMovement {
  id: number;
  product_id: number;
  movement_type: string;
  quantity: string;
  unit: Unit;
  previous_quantity: string;
  new_quantity: string;
  reason: string;
  reference_type: string | null;
  reference_id: number | null;
  created_at: string;
}
