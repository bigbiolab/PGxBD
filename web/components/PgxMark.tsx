import { useId } from "react";

export default function PgxMark({ className = "h-7 w-7" }: { className?: string }) {
  const clipId = useId();

  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
      <rect x="1" y="1" width="30" height="30" rx="7" fill="#eef1f4" stroke="#c7ccd3" strokeWidth="1" />
      {/* DNA bowtie */}
      <path d="M5,4 L5,15 L16,9.5 Z" fill="#f2b705" />
      <path d="M27,4 L27,15 L16,9.5 Z" fill="#f2b705" />
      {/* two-tone capsule */}
      <defs>
        <clipPath id={clipId}>
          <rect x="0" y="-6" width="9" height="12" />
        </clipPath>
      </defs>
      <g transform="translate(16,22) rotate(-35)">
        <rect x="-7.5" y="-3.75" width="15" height="7.5" rx="3.75" fill="#3fae5a" />
        <rect x="-7.5" y="-3.75" width="15" height="7.5" rx="3.75" fill="#e6584f" clipPath={`url(#${clipId})`} />
      </g>
    </svg>
  );
}
