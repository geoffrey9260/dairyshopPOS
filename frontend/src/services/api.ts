import type {
  Category,
  DashboardReport,
  Expense,
  ExpenseCategory,
  PaymentMethod,
  Product,
  Sale,
  StockMovement,
  Unit,
} from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";
const API_HOST = import.meta.env.VITE_API_HOST;
const API_BASE_URL = API_HOST
  ? `https://${String(API_HOST).replace(/^https?:\/\//, "").replace(/\/$/, "")}/api`
  : API_URL;

export class ApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options,
  });
  if (!response.ok) {
    let message = "Request failed";
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      message = response.statusText;
    }
    throw new ApiError(message);
  }
  return response.json() as Promise<T>;
}

export interface ProductPayload {
  name: string;
  category_id: number;
  unit: Unit;
  selling_price: string;
  buying_price?: string | null;
  minimum_stock: string;
  current_stock?: string;
  average_cost?: string | null;
}

export interface CartItemPayload {
  product_id: number;
  mode: "quantity" | "amount";
  quantity?: string;
  unit: Unit;
  amount?: string;
}

export const api = {
  settings: () => request<Record<string, string>>("/settings"),
  saveSetting: (key: string, value: string) => request(`/settings/${key}`, { method: "PUT", body: JSON.stringify({ value }) }),
  categories: () => request<Category[]>("/categories"),
  createCategory: (name: string) => request<Category>("/categories", { method: "POST", body: JSON.stringify({ name }) }),
  products: (activeOnly = false) => request<Product[]>(`/products?include_inactive=${activeOnly ? "false" : "true"}`),
  createProduct: (payload: ProductPayload) => request<Product>("/products", { method: "POST", body: JSON.stringify(payload) }),
  updateProduct: (id: number, payload: ProductPayload) =>
    request<Product>(`/products/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deactivateProduct: (id: number) => request<Product>(`/products/${id}/deactivate`, { method: "PATCH" }),
  reactivateProduct: (id: number) => request<Product>(`/products/${id}/reactivate`, { method: "PATCH" }),
  sales: () => request<Sale[]>("/sales"),
  createSale: (items: CartItemPayload[], payment_method: PaymentMethod) =>
    request<Sale>("/sales", { method: "POST", body: JSON.stringify({ items, payment_method }) }),
  dashboard: () => request<DashboardReport>("/dashboard"),
  receiveStock: (payload: { items: Array<{ product_id: number; quantity: string; unit: Unit; unit_cost: string }>; notes?: string }) =>
    request("/inventory/receive", { method: "POST", body: JSON.stringify(payload) }),
  stockCount: (payload: { product_id: number; counted_quantity: string; unit: Unit; reason: string }) =>
    request("/inventory/count", { method: "POST", body: JSON.stringify(payload) }),
  movements: () => request<StockMovement[]>("/inventory/movements"),
  expenseCategories: () => request<ExpenseCategory[]>("/expense-categories"),
  createExpenseCategory: (name: string) =>
    request<ExpenseCategory>("/expense-categories", { method: "POST", body: JSON.stringify({ name }) }),
  expenses: (start?: string, end?: string) => request<Expense[]>(`/expenses?${new URLSearchParams({ ...(start ? { start_date: start } : {}), ...(end ? { end_date: end } : {}) })}`),
  createExpense: (payload: { category_id: number; amount: string; description: string; expense_date: string; notes?: string }) =>
    request<Expense>("/expenses", { method: "POST", body: JSON.stringify(payload) }),
  dailyReport: (day?: string) => request(`/reports/daily${day ? `?day=${day}` : ""}`),
  weeklyReport: (start?: string) => request(`/reports/weekly${start ? `?start_date=${start}` : ""}`),
  monthlyReport: (year?: number, month?: number) =>
    request(`/reports/monthly?${new URLSearchParams({ ...(year ? { year: String(year) } : {}), ...(month ? { month: String(month) } : {}) })}`),
  productReport: (start?: string, end?: string) =>
    request(`/reports/products?${new URLSearchParams({ ...(start ? { start_date: start } : {}), ...(end ? { end_date: end } : {}) })}`),
  milkReport: (start?: string, end?: string, productId?: number) =>
    request(`/reports/milk?${new URLSearchParams({ ...(start ? { start_date: start } : {}), ...(end ? { end_date: end } : {}), ...(productId ? { product_id: String(productId) } : {}) })}`),
  inventoryReport: () => request<Array<Record<string, string | number>>>("/reports/inventory"),
  expenseReport: (start?: string, end?: string) =>
    request(`/reports/expenses?${new URLSearchParams({ ...(start ? { start_date: start } : {}), ...(end ? { end_date: end } : {}) })}`),
};
