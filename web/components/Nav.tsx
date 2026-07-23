"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/overview", label: "Overview" },
  { href: "/genes", label: "Genes" },
  { href: "/frequencies", label: "Frequencies" },
  { href: "/phenotypes", label: "Phenotypes" },
  { href: "/drugs", label: "Drugs" },
  { href: "/variants", label: "Variants" },
  { href: "/visualizations", label: "Visualizations" },
];

export default function Nav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 border-b border-border bg-surface/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2 shrink-0">
          <span className="flex h-7 w-7 items-center justify-center rounded-md bg-accent text-[13px] font-bold text-accent-foreground">
            P
          </span>
          <span className="text-sm font-semibold tracking-tight">PGxBD</span>
        </Link>
        <nav className="flex flex-1 gap-1 overflow-x-auto text-sm">
          {LINKS.map((link) => {
            const active =
              link.href === "/" ? pathname === "/" : pathname.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`whitespace-nowrap rounded-md px-3 py-1.5 transition-colors ${
                  active
                    ? "bg-surface-muted text-foreground font-medium"
                    : "text-muted hover:text-foreground"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
