export const units = ["Piece", "Millilitre", "Litre", "Gram", "Kilogram", "Pack", "Bottle", "Box"] as const;
export const paymentMethods = ["Cash", "M-Pesa"] as const;

export function money(value: string | number | null | undefined) {
  const numeric = Number(value ?? 0);
  return `KSh ${numeric.toLocaleString("en-KE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function qty(value: string | number | null | undefined, unit?: string) {
  const numeric = Number(value ?? 0);
  const formatted = numeric.toLocaleString("en-KE", { maximumFractionDigits: 3 });
  return unit ? `${formatted} ${unit}` : formatted;
}

export function todayIso() {
  return new Date().toISOString().slice(0, 10);
}
