import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPrice(price: number): string {
  if (price >= 1000) return price.toFixed(2);
  if (price >= 1) return price.toFixed(4);
  return price.toFixed(6);
}

export function formatPercent(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}%`;
}

export function scoreColor(score: number): string {
  if (score >= 50) return "text-emerald-400";
  if (score >= 20) return "text-lime-400";
  if (score <= -50) return "text-red-400";
  if (score <= -20) return "text-orange-400";
  return "text-yellow-400";
}

export function scoreBg(score: number): string {
  if (score >= 50) return "bg-emerald-500/20 border-emerald-500/40";
  if (score >= 20) return "bg-lime-500/20 border-lime-500/40";
  if (score <= -50) return "bg-red-500/20 border-red-500/40";
  if (score <= -20) return "bg-orange-500/20 border-orange-500/40";
  return "bg-yellow-500/20 border-yellow-500/40";
}
