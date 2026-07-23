export default function Badge({
  children,
  color,
}: {
  children: React.ReactNode;
  color?: string;
}) {
  return (
    <span
      className="inline-flex items-center rounded-md border border-border px-2 py-0.5 text-xs font-medium"
      style={color ? { color, borderColor: color } : undefined}
    >
      {children}
    </span>
  );
}
