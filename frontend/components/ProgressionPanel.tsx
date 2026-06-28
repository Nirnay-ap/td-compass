"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { ProgressionCandidate, Role } from "@/lib/types";
import { Card } from "./ui";

export function ProgressionPanel({
  role,
  manager,
  onSelect,
}: {
  role: Role;
  manager: string;
  onSelect: (id: string) => void;
}) {
  const [candidates, setCandidates] = useState<ProgressionCandidate[]>([]);
  const [onlyReady, setOnlyReady] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .progression(role === "Project Manager" ? manager : undefined, onlyReady)
      .then((d) => {
        if (!cancelled) {
          setCandidates(d.candidates);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [role, manager, onlyReady]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-slate-800">
            Career Progression Readiness
          </h2>
          <p className="text-sm text-slate-500">
            Scored against the promotion policy: learning hours, an E2 competency,
            performance, and tenure.
          </p>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-600">
          <input
            type="checkbox"
            checked={onlyReady}
            onChange={(e) => setOnlyReady(e.target.checked)}
          />
          Only fully-ready
        </label>
      </div>

      {loading ? (
        <p className="text-sm text-slate-500">Loading…</p>
      ) : (
        <div className="grid gap-3 lg:grid-cols-2">
          {candidates.map((c) => (
            <Card key={c.associate_id} className="p-4">
              <button onClick={() => onSelect(c.associate_id)} className="w-full text-left">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-slate-900">{c.associate_name}</div>
                    <div className="text-xs text-slate-500">
                      {c.designation} · {c.band}
                    </div>
                  </div>
                  <div
                    className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                      c.ready
                        ? "bg-emerald-100 text-emerald-700"
                        : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {c.ready ? "Ready" : `${c.readiness_score}/${c.max_score}`}
                  </div>
                </div>
                <div className="mt-3 flex gap-1.5">
                  {Array.from({ length: c.max_score }).map((_, i) => (
                    <div
                      key={i}
                      className={`h-1.5 flex-1 rounded-full ${
                        i < c.readiness_score ? "bg-indigo-500" : "bg-slate-200"
                      }`}
                    />
                  ))}
                </div>
                <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-slate-600">
                  <Metric label="Learning" value={`${c.ytd_learning_hours}/${c.ytd_target_hours}`} />
                  <Metric label="E2 comps" value={String(c.e2_competencies)} />
                  <Metric label="Rating" value={c.performance_rating.split(" ")[0]} />
                </div>
                {c.gaps.length > 0 && (
                  <div className="mt-3 text-xs text-amber-700">
                    Gaps: {c.gaps.join("; ")}
                  </div>
                )}
              </button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-slate-50 p-2 text-center">
      <div className="text-[10px] uppercase tracking-wide text-slate-400">{label}</div>
      <div className="font-semibold text-slate-800">{value}</div>
    </div>
  );
}
