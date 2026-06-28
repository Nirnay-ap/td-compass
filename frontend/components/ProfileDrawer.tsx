"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Associate } from "@/lib/types";
import { LevelBadge, ProgressBar, StatusBadge } from "./ui";

export function ProfileDrawer({
  associateId,
  onClose,
}: {
  associateId: string | null;
  onClose: () => void;
}) {
  const [data, setData] = useState<Associate | null>(null);

  useEffect(() => {
    if (!associateId) return;
    let cancelled = false;
    api.associate(associateId).then((d) => {
      if (!cancelled) setData(d);
    });
    return () => {
      cancelled = true;
    };
  }, [associateId]);

  if (!associateId) return null;

  const ready = data?.id === associateId;
  const loading = !ready;

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <div className="absolute inset-0 bg-slate-900/30" onClick={onClose} />
      <div className="relative z-50 h-full w-full max-w-xl overflow-y-auto bg-white shadow-2xl">
        <div className="sticky top-0 flex items-center justify-between border-b border-slate-200 bg-white px-5 py-4">
          <h2 className="text-base font-semibold text-slate-800">Associate Profile</h2>
          <button
            onClick={onClose}
            className="rounded-lg px-2 py-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
          >
            ✕
          </button>
        </div>

        {loading && <div className="p-6 text-sm text-slate-500">Loading…</div>}

        {ready && data && (
          <div className="space-y-6 p-5">
            <header>
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 text-lg font-semibold text-indigo-700">
                  {data.name.split(" ").map((n) => n[0]).join("")}
                </div>
                <div>
                  <div className="text-lg font-semibold text-slate-900">{data.name}</div>
                  <div className="text-sm text-slate-500">
                    {data.designation} · {data.band} · {data.id}
                  </div>
                </div>
              </div>
              <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                <Field label="Project" value={data.project} />
                <Field label="Department" value={data.department} />
                <Field label="Project Manager" value={data.project_manager} />
                <Field label="TD Manager" value={data.td_manager} />
                <Field label="Location" value={data.location} />
                <Field label="Experience" value={`${data.total_experience_years} yrs`} />
                <Field label="Performance" value={data.performance_rating} />
                <Field label="Joined" value={data.date_of_joining} />
              </dl>
            </header>

            <section>
              <SectionTitle>Learning Hours (YTD)</SectionTitle>
              <div className="mt-2 flex items-center gap-3">
                <div className="flex-1">
                  <ProgressBar value={data.ytd_learning_hours} target={data.ytd_target_hours} />
                </div>
                <span className="text-sm font-medium text-slate-700">
                  {data.ytd_learning_hours} / {data.ytd_target_hours} hrs
                </span>
              </div>
              <div className="mt-3 grid grid-cols-4 gap-2">
                {data.learning_hours.map((l) => (
                  <div key={l.quarter} className="rounded-lg bg-slate-50 p-2 text-center">
                    <div className="text-xs text-slate-500">{l.quarter}</div>
                    <div className="text-sm font-semibold text-slate-800">{l.hours}</div>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <SectionTitle>
                Competencies · E1: {data.e1_competencies} · E2: {data.e2_competencies}
              </SectionTitle>
              <div className="mt-2 space-y-2">
                {data.competencies.map((c) => (
                  <div
                    key={c.name}
                    className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 px-3 py-2"
                  >
                    <div className="flex items-center gap-2">
                      <LevelBadge level={c.level} />
                      <div>
                        <div className="text-sm font-medium text-slate-800">{c.name}</div>
                        <div className="text-xs text-slate-500">
                          {c.category}
                          {c.expiry_date ? ` · expires ${c.expiry_date}` : " · no expiry"}
                        </div>
                      </div>
                    </div>
                    <StatusBadge status={c.status} />
                  </div>
                ))}
              </div>
            </section>

            <section>
              <SectionTitle>Certifications</SectionTitle>
              <div className="mt-2 space-y-2">
                {data.certifications.map((c) => (
                  <div
                    key={c.name}
                    className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 px-3 py-2"
                  >
                    <div className="flex items-center gap-2">
                      <LevelBadge level={c.type} />
                      <div>
                        <div className="text-sm font-medium text-slate-800">{c.name}</div>
                        <div className="text-xs text-slate-500">
                          {c.provider}
                          {c.expiry_date ? ` · expires ${c.expiry_date}` : " · no expiry"}
                        </div>
                      </div>
                    </div>
                    <StatusBadge status={c.status} />
                  </div>
                ))}
              </div>
            </section>

            <section>
              <SectionTitle>Upcoming TD Programs</SectionTitle>
              {data.upcoming_td_programs.length === 0 ? (
                <p className="mt-2 text-sm text-slate-500">No upcoming nominations.</p>
              ) : (
                <div className="mt-2 space-y-2">
                  {data.upcoming_td_programs.map((p) => (
                    <div
                      key={p.name}
                      className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 px-3 py-2"
                    >
                      <div>
                        <div className="text-sm font-medium text-slate-800">{p.name}</div>
                        <div className="text-xs text-slate-500">
                          {p.start_date} · {p.mode} · {p.duration_days}d
                        </div>
                      </div>
                      <span className="rounded-full border border-slate-200 bg-white px-2 py-0.5 text-xs text-slate-600">
                        {p.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-slate-400">{label}</dt>
      <dd className="text-slate-700">{value}</dd>
    </div>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
      {children}
    </h3>
  );
}
