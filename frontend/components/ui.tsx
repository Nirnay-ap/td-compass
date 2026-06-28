import type { ItemStatus } from "@/lib/types";

export function StatusBadge({ status }: { status: ItemStatus }) {
  const map: Record<ItemStatus, string> = {
    Active: "bg-emerald-100 text-emerald-700 border-emerald-200",
    "Expiring Soon": "bg-amber-100 text-amber-700 border-amber-200",
    Expired: "bg-rose-100 text-rose-700 border-rose-200",
  };
  return (
    <span className={`inline-block rounded-full border px-2 py-0.5 text-xs font-medium ${map[status]}`}>
      {status}
    </span>
  );
}

export function LevelBadge({ level }: { level: string }) {
  const isE2 = level === "E2";
  const isExternal = level === "External";
  const cls = isE2
    ? "bg-indigo-100 text-indigo-700 border-indigo-200"
    : isExternal
      ? "bg-sky-100 text-sky-700 border-sky-200"
      : "bg-slate-100 text-slate-600 border-slate-200";
  return (
    <span className={`inline-block rounded border px-1.5 py-0.5 text-[11px] font-semibold ${cls}`}>
      {level}
    </span>
  );
}

export function Card({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}>
      {children}
    </div>
  );
}

export function Stat({
  label,
  value,
  sub,
  accent = "text-slate-900",
}: {
  label: string;
  value: string | number;
  sub?: string;
  accent?: string;
}) {
  return (
    <Card className="p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div className={`mt-1 text-2xl font-semibold ${accent}`}>{value}</div>
      {sub && <div className="mt-0.5 text-xs text-slate-500">{sub}</div>}
    </Card>
  );
}

export function ProgressBar({ value, target }: { value: number; target: number }) {
  const pct = Math.min(100, Math.round((value / Math.max(1, target)) * 100));
  const color = pct >= 100 ? "bg-emerald-500" : pct >= 60 ? "bg-amber-500" : "bg-rose-500";
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
      <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}
