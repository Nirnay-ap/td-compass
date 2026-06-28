"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { Associate, Role } from "@/lib/types";
import { Card, LevelBadge, ProgressBar } from "./ui";

export function PeoplePanel({
  role,
  manager,
  onSelect,
}: {
  role: Role;
  manager: string;
  onSelect: (id: string) => void;
}) {
  const [people, setPeople] = useState<Associate[]>([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .associates(role === "Project Manager" ? manager : undefined)
      .then((d) => {
        if (!cancelled) {
          setPeople(d.associates);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [role, manager]);

  const filtered = useMemo(() => {
    const q = filter.toLowerCase();
    return people.filter((p) =>
      [p.name, p.designation, p.band, p.project, p.department].join(" ").toLowerCase().includes(q),
    );
  }, [people, filter]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Search by name, project, band, skill area…"
          className="w-full max-w-md rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
        />
        <span className="ml-3 whitespace-nowrap text-sm text-slate-500">
          {filtered.length} associate{filtered.length === 1 ? "" : "s"}
        </span>
      </div>

      {loading ? (
        <p className="text-sm text-slate-500">Loading…</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((p) => (
            <Card key={p.id} className="p-4 transition hover:border-indigo-300 hover:shadow">
              <button onClick={() => onSelect(p.id)} className="w-full text-left">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
                    {p.name.split(" ").map((n) => n[0]).join("")}
                  </div>
                  <div className="min-w-0">
                    <div className="truncate font-medium text-slate-900">{p.name}</div>
                    <div className="truncate text-xs text-slate-500">
                      {p.designation} · {p.band}
                    </div>
                  </div>
                </div>
                <div className="mt-3 text-xs text-slate-500">{p.project}</div>
                <div className="mt-2">
                  <div className="flex justify-between text-xs text-slate-500">
                    <span>Learning hrs</span>
                    <span>
                      {p.ytd_learning_hours}/{p.ytd_target_hours}
                    </span>
                  </div>
                  <div className="mt-1">
                    <ProgressBar value={p.ytd_learning_hours} target={p.ytd_target_hours} />
                  </div>
                </div>
                <div className="mt-3 flex items-center gap-2">
                  <span className="text-xs text-slate-500">Competencies</span>
                  <LevelBadge level="E1" /> {p.e1_competencies}
                  <LevelBadge level="E2" /> {p.e2_competencies}
                </div>
              </button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
