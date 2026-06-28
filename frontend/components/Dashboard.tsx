"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { OrgSummary, ReminderItem, Role } from "@/lib/types";
import { Card, Stat } from "./ui";

export function Dashboard({
  role,
  manager,
  onSelect,
  goToReminders,
}: {
  role: Role;
  manager: string;
  onSelect: (id: string) => void;
  goToReminders: () => void;
}) {
  const [summary, setSummary] = useState<OrgSummary | null>(null);
  const [topReminders, setTopReminders] = useState<ReminderItem[]>([]);
  const [teamSize, setTeamSize] = useState<number | null>(null);

  useEffect(() => {
    api.summary().then(setSummary);
    const mgr = role === "Project Manager" ? manager : undefined;
    api.reminders(mgr, 90).then((d) => {
      setTopReminders([...d.expired, ...d.expiring_soon].slice(0, 6));
    });
    if (role === "Project Manager") {
      api.associates(manager).then((d) => setTeamSize(d.count));
    }
  }, [role, manager]);

  if (!summary) return <p className="text-sm text-slate-500">Loading…</p>;

  return (
    <div className="space-y-5">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Stat
          label={role === "Project Manager" ? "My Team" : "Total Headcount"}
          value={role === "Project Manager" ? (teamSize ?? "…") : summary.headcount.total}
          sub={role === "Project Manager" ? `Managed by ${manager}` : "Across all projects"}
        />
        <Stat
          label="Avg Learning Hours"
          value={summary.avg_ytd_learning_hours}
          sub="YTD per associate (target 160)"
          accent="text-indigo-600"
        />
        <Stat
          label="E2 Competencies"
          value={summary.total_e2_competencies}
          sub={`${summary.total_e1_competencies} at E1 level`}
          accent="text-violet-600"
        />
        <Stat
          label="Expiring / Expired"
          value={summary.items_expiring_or_expired}
          sub="Competencies & certifications"
          accent="text-rose-600"
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="p-4">
          <h3 className="text-sm font-semibold text-slate-700">Headcount by Project</h3>
          <div className="mt-3 space-y-2">
            {Object.entries(summary.headcount.by_project)
              .sort((a, b) => b[1] - a[1])
              .map(([proj, n]) => (
                <div key={proj}>
                  <div className="flex justify-between text-xs text-slate-600">
                    <span className="truncate">{proj}</span>
                    <span>{n}</span>
                  </div>
                  <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full bg-indigo-500"
                      style={{ width: `${(n / summary.headcount.total) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">Urgent Reminders</h3>
            <button
              onClick={goToReminders}
              className="text-xs font-medium text-indigo-600 hover:underline"
            >
              View all →
            </button>
          </div>
          <div className="mt-3 space-y-2">
            {topReminders.length === 0 && (
              <p className="text-sm text-slate-500">No upcoming expiries. 🎉</p>
            )}
            {topReminders.map((i, idx) => (
              <button
                key={idx}
                onClick={() => onSelect(i.associate_id)}
                className="flex w-full items-center justify-between rounded-lg border border-slate-100 px-3 py-2 text-left hover:bg-slate-50"
              >
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium text-slate-800">{i.name}</div>
                  <div className="truncate text-xs text-slate-500">{i.associate_name}</div>
                </div>
                <span
                  className={`ml-2 whitespace-nowrap text-xs font-medium ${
                    i.days_to_expiry < 0 ? "text-rose-600" : "text-amber-600"
                  }`}
                >
                  {i.days_to_expiry < 0
                    ? `${Math.abs(i.days_to_expiry)}d overdue`
                    : `in ${i.days_to_expiry}d`}
                </span>
              </button>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
