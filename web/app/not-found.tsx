import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center gap-3 py-24 text-center">
      <p className="text-sm font-medium text-accent">404</p>
      <h1 className="text-2xl font-semibold tracking-tight">Not found</h1>
      <p className="max-w-sm text-sm text-muted">
        That gene, variant, or page doesn&apos;t exist in the PGxBD database.
      </p>
      <Link href="/" className="mt-2 text-sm text-accent hover:underline">
        Back to overview
      </Link>
    </div>
  );
}
