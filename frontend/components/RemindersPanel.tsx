"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { ReminderItem, Role } from "@/lib/types";
import { Card, LevelBadge, StatusBadge } from "./ui";

export function RemindersPanel({
  role,
  manager,
  onSelect,
}: {
  role: Role;
  manager: string;
  onSelect: (id: string) => void;
}) {
  const [expired, setExpired] = useState<ReminderItem[]>([]);
  const [soon, setSoon] = useState<ReminderItem[]>([]);
  const [windowDays, setWindowDays] = useState(90);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .reminders(role === "Project Manager" ? manager : undefined, windowDays)
      .then((d) => {
        if (!cancelled) {
          setExpired(d.expired);
          setSoon(d.expiring_soon);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [role, manager, windowDays]);

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-slate-800">
            Competency &amp; Certification Reminders
          </h2>
          <p className="text-sm text-slate-500">
            Proactive alerts so renewals never lapse. {expired.length} expired ·{" "}
            {soon.length} expiring soon.
          </p>
        </div>
        <select
          value={windowDays}
          onChange={(e) => setWindowDays(Number(e.target.value))}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value={30}>Next 30 days</option>
          <option value={60}>Next 60 days</option>
          <option value={90}>Next 90 days</option>
          <option value={180}>Next 180 days</option>
        </select>
      </div>

      {loading ? (
        <p className="text-sm text-slate-500">Loading…</p>
      ) : (
        <>
          <ReminderGroup
            title="Expired — action needed"
            tone="rose"
            items={expired}
            onSelect={onSelect}
          />
          <ReminderGroup
            title="Expiring soon"
            tone="amber"
            items={soon}
            onSelect={onSelect}
          />
        </>
      )}
    </div>
  );
}

function ReminderGroup({
  title,
  tone,
  items,
  onSelect,
}: {
  title: string;
  tone: "rose" | "amber";
  items: ReminderItem[];
  onSelect: (id: string) => void;
}) {
  const dot = tone === "rose" ? "bg-rose-500" : "bg-amber-500";
  return (
    <Card className="overflow-hidden">
      <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3">
        <span className={`h-2.5 w-2.5 rounded-full ${dot}`} />
        <h3 className="text-sm font-semibold text-slate-700">{title}</h3>
        <span className="text-xs text-slate-400">({items.length})</span>
      </div>
      {items.length === 0 ? (
        <p className="px-4 py-4 text-sm text-slate-500">Nothing here. 🎉</p>
      ) : (
        <div className="divide-y divide-slate-100">
          {items.map((i, idx) => (
            <button
              key={`${i.associate_id}-${i.name}-${idx}`}
              onClick={() => onSelect(i.associate_id)}
              className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-slate-50"
            >
              <div className="flex items-center gap-3">
                <LevelBadge level={i.level} />
                <div>
                  <div className="text-sm font-medium text-slate-800">{i.name}</div>
                  <div className="text-xs text-slate-500">
                    {i.associate_name} · {i.item_type} · {i.project}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <StatusBadge status={i.status} />
                <div className="mt-1 text-xs text-slate-500">
                  {i.days_to_expiry < 0
                    ? `${Math.abs(i.days_to_expiry)}d ago`
                    : `in ${i.days_to_expiry}d`}{" "}
                  · {i.expiry_date}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </Card>
  );
}
