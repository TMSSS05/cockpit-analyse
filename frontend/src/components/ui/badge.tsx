import { cn } from "@/lib/utils";
import { forwardRef } from "react";

const variants = {
  default: "bg-zinc-800 text-zinc-200",
  buy: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  sell: "bg-red-500/20 text-red-400 border-red-500/30",
  neutral: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  strong_buy: "bg-emerald-500/30 text-emerald-300 border-emerald-500/50",
  strong_sell: "bg-red-500/30 text-red-300 border-red-500/50",
  info: "bg-blue-500/20 text-blue-400 border-blue-500/30",
} as const;

interface BadgeProps {
  variant?: keyof typeof variants;
  className?: string;
  children: React.ReactNode;
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = "default", className, children }, ref) => (
    <span
      ref={ref}
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  )
);
Badge.displayName = "Badge";

export { Badge };
