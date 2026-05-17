import Link from "next/link";
import type { ComponentPropsWithoutRef, ReactNode } from "react";
import { cn } from "@/lib/utils";

type ButtonProps = ComponentPropsWithoutRef<"button"> & {
  variant?: "default" | "outline" | "ghost";
};

export function Button({ className, variant = "default", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-10 items-center justify-center rounded-md px-4 text-sm font-medium transition disabled:pointer-events-none disabled:opacity-50",
        variant === "default" && "bg-black text-white hover:bg-black/90",
        variant === "outline" && "border border-black/15 bg-white text-black hover:border-black/35",
        variant === "ghost" && "text-black/70 hover:bg-black/5 hover:text-black",
        className
      )}
      {...props}
    />
  );
}

type ButtonLinkProps = {
  href: string;
  children: ReactNode;
  className?: string;
  variant?: "default" | "outline" | "ghost";
};

export function ButtonLink({ href, children, className, variant = "default" }: ButtonLinkProps) {
  return (
    <Link
      href={href}
      className={cn(
        "inline-flex h-10 items-center justify-center rounded-md px-4 text-sm font-medium transition",
        variant === "default" && "bg-black text-white hover:bg-black/90",
        variant === "outline" && "border border-black/15 bg-white text-black hover:border-black/35",
        variant === "ghost" && "text-black/70 hover:bg-black/5 hover:text-black",
        className
      )}
    >
      {children}
    </Link>
  );
}
