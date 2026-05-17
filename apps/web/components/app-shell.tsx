"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/projects/new", label: "New Project" }
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-mist text-ink">
      <div className="mx-auto flex min-h-screen max-w-[1600px]">
        <aside className="hidden w-[260px] shrink-0 border-r border-black/8 bg-[#f7f7f3] lg:flex lg:flex-col">
          <div className="border-b border-black/8 px-8 py-8">
            <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Auto Video</div>
            <h1 className="mt-3 max-w-[160px] text-[28px] font-semibold leading-[1.05]">
              Industrial video console
            </h1>
          </div>
          <nav className="flex flex-1 flex-col gap-2 px-4 py-6">
            {navItems.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between rounded-md border px-4 py-3 text-sm transition ${
                    active
                      ? "border-black bg-black text-white"
                      : "border-black/10 bg-panel text-black hover:border-black/25"
                  }`}
                >
                  <span>{item.label}</span>
                  <span className="font-mono text-[11px] uppercase tracking-[0.24em]">
                    {active ? "Open" : "View"}
                  </span>
                </Link>
              );
            })}
          </nav>
          <div className="border-t border-black/8 p-4">
            <div className="rounded-md border border-black/10 bg-panel p-4">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Pipeline</div>
              <div className="mt-3 space-y-2 text-sm text-black/78">
                <div>1. Deconstruct</div>
                <div>2. Rewrite</div>
                <div>3. Match</div>
                <div>4. Preview render</div>
                <div>5. Publish copy</div>
              </div>
            </div>
          </div>
        </aside>
        <div className="flex min-h-screen flex-1 flex-col">
          <header className="sticky top-0 z-20 border-b border-black/8 bg-mist/88 backdrop-blur">
            <div className="flex items-center justify-between px-6 py-4 lg:px-10">
              <div>
                <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">
                  Research TikTok Workflow
                </div>
                <div className="mt-1 text-sm text-black/62">
                  Reference analysis, script rewrite, shot matching, captioned preview render, publishing copy.
                </div>
              </div>
              <Link
                href="/projects/new"
                className="rounded-md border border-black bg-black px-4 py-2 text-sm font-medium text-white transition hover:bg-black/90"
              >
                New Project
              </Link>
            </div>
          </header>
          <main className="flex-1 px-4 py-6 lg:px-10 lg:py-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
