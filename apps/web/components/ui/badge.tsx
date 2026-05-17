import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Badge({
  children,
  className,
  variant = "secondary"
}: {
  children: ReactNode;
  className?: string;
  variant?: "default" | "secondary" | "outline";
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.18em]",
        variant === "default" && "bg-black text-white",
        variant === "secondary" && "bg-black/[0.06] text-black/62",
        variant === "outline" && "border border-black/15 bg-white text-black/62",
        className
      )}
    >
      {children}
    </span>
  );
}
