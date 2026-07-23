"use client";

import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useTransition } from "react";

export type FilterField = {
  name: string;
  label: string;
  type: "select" | "text";
  options?: { value: string; label: string }[];
  placeholder?: string;
};

export default function FilterBar({ fields }: { fields: FilterField[] }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  function update(name: string, value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) params.set(name, value);
    else params.delete(name);
    startTransition(() => {
      router.push(`${pathname}?${params.toString()}`);
    });
  }

  const hasActiveFilters = fields.some((f) => searchParams.get(f.name));

  return (
    <div
      className={`flex flex-wrap items-end gap-3 rounded-xl border border-border bg-surface p-4 transition-opacity ${
        isPending ? "opacity-60" : ""
      }`}
    >
      {fields.map((field) => (
        <label key={field.name} className="flex flex-col gap-1 text-xs text-muted">
          {field.label}
          {field.type === "select" ? (
            <select
              defaultValue={searchParams.get(field.name) ?? ""}
              onChange={(e) => update(field.name, e.target.value)}
              className="min-w-[9rem] rounded-md border border-border bg-background px-2 py-1.5 text-sm text-foreground"
            >
              <option value="">All</option>
              {field.options?.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              defaultValue={searchParams.get(field.name) ?? ""}
              placeholder={field.placeholder}
              onBlur={(e) => update(field.name, e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") update(field.name, e.currentTarget.value);
              }}
              className="min-w-[9rem] rounded-md border border-border bg-background px-2 py-1.5 text-sm text-foreground"
            />
          )}
        </label>
      ))}
      {hasActiveFilters && (
        <button
          onClick={() => router.push(pathname)}
          className="rounded-md px-3 py-1.5 text-xs text-muted underline-offset-2 hover:text-foreground hover:underline"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
