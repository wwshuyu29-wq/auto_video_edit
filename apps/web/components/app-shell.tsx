"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const navItems = [
  { href: "/", label: "How it works" },
  { href: "/projects/new", label: "Start" }
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[#eef4f1] text-ink">
      <header className="sticky top-0 z-30 border-b border-ink/10 bg-[#eef4f1]/92 backdrop-blur">
        <div className="mx-auto flex max-w-[1180px] items-center justify-between px-5 py-4 lg:px-8">
          <Link href="/" className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-md bg-ink text-sm font-semibold text-white">
              AV
            </span>
            <span>
              <span className="block text-sm font-semibold leading-none">Auto Video</span>
              <span className="mt-1 block text-xs text-ink/50">TikTok workflow builder</span>
            </span>
          </Link>

          <nav className="flex items-center gap-2">
            {navItems.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded-md px-3 py-2 text-sm font-medium transition ${
                    active ? "bg-white text-ink shadow-[0_8px_24px_rgba(31,46,43,0.06)]" : "text-ink/62 hover:text-ink"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </header>

      <main className="mx-auto min-h-screen max-w-[1180px] px-5 py-8 lg:px-8 lg:py-10">{children}</main>
    </div>
  );
}
