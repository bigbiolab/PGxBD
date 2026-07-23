"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center gap-3 py-24 text-center">
      <p className="text-sm font-medium text-red-500">Error</p>
      <h1 className="text-2xl font-semibold tracking-tight">Couldn&apos;t reach the PGxBD API</h1>
      <p className="max-w-md text-sm text-muted">
        {error.message || "The API request failed."} Make sure the API is running at{" "}
        <code className="rounded bg-surface-muted px-1 py-0.5">
          uvicorn api.main:app --reload --port 8000
        </code>
        .
      </p>
      <button
        onClick={() => reset()}
        className="mt-2 rounded-md border border-border px-3 py-1.5 text-sm hover:border-accent hover:text-accent"
      >
        Retry
      </button>
    </div>
  );
}
