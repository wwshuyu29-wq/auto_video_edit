import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <section className={cn("border border-black/10 bg-panel shadow-panel", className)}>{children}</section>;
}

export function CardHeader({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("border-b border-black/10 p-5", className)}>{children}</div>;
}

export function CardContent({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("p-5", className)}>{children}</div>;
}

export function CardTitle({ children, className }: { children: ReactNode; className?: string }) {
  return <h2 className={cn("text-xl font-semibold tracking-[-0.04em]", className)}>{children}</h2>;
}

export function CardDescription({ children, className }: { children: ReactNode; className?: string }) {
  return <p className={cn("mt-2 text-sm leading-6 text-black/62", className)}>{children}</p>;
}
