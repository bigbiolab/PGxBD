export default function MarkTooltip({
  children,
  tooltip,
  className = "",
  style,
}: {
  children: React.ReactNode;
  tooltip: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}) {
  return (
    <div
      tabIndex={0}
      className={`group/mark relative outline-none ${className}`}
      style={style}
    >
      {children}
      <div
        role="tooltip"
        className="pointer-events-none absolute bottom-full left-1/2 z-30 mb-2 w-max max-w-[16rem] -translate-x-1/2 rounded-md border border-border bg-surface px-2.5 py-1.5 text-xs opacity-0 shadow-lg transition-opacity duration-100 group-hover/mark:opacity-100 group-focus/mark:opacity-100"
      >
        {tooltip}
      </div>
    </div>
  );
}
