"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Role } from "@/lib/types";
import { ChatPanel } from "@/components/ChatPanel";
import { Dashboard } from "@/components/Dashboard";
import { PeoplePanel } from "@/components/PeoplePanel";
import { ProfileDrawer } from "@/components/ProfileDrawer";
import { ProgressionPanel } from "@/components/ProgressionPanel";
import { RemindersPanel } from "@/components/RemindersPanel";

type Tab = "Assistant" | "Dashboard" | "People" | "Reminders" | "Progression";
const TABS: Tab[] = ["Assistant", "Dashboard", "People", "Reminders", "Progression"];

export default function Home() {
  const [role, setRole] = useState<Role>("TD Manager");
  const [tab, setTab] = useState<Tab>("Assistant");
  const [managers, setManagers] = useState<{ project: string[]; td: string[] }>({
    project: [],
    td: [],
  });
  const [pm, setPm] = useState("");
  const [tdm, setTdm] = useState("");
  const [provider, setProvider] = useState("rule-based");
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    api.managers().then((d) => {
      setManagers({ project: d.project_managers, td: d.td_managers });
      setPm(d.project_managers[0] ?? "");
      setTdm(d.td_managers[0] ?? "");
    });
    api.health().then((d) => setProvider(d.llm_provider));
  }, []);

  const manager = role === "Project Manager" ? pm : tdm;

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white">
              <span className="text-lg font-bold">◆</span>
            </div>
            <div>
              <div className="text-lg font-semibold leading-tight text-slate-900">
                TD Compass
              </div>
              <div className="text-xs text-slate-500">
                Talent Development Intelligence
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex rounded-lg border border-slate-200 bg-slate-50 p-0.5">
              {(["TD Manager", "Project Manager"] as Role[]).map((r) => (
                <button
                  key={r}
                  onClick={() => setRole(r)}
                  className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                    role === r
                      ? "bg-white text-indigo-700 shadow-sm"
                      : "text-slate-500 hover:text-slate-700"
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
            {role === "Project Manager" ? (
              <select
                value={pm}
                onChange={(e) => setPm(e.target.value)}
                className="rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
              >
                {managers.project.map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            ) : (
              <select
                value={tdm}
                onChange={(e) => setTdm(e.target.value)}
                className="rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
              >
                {managers.td.map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            )}
          </div>
        </div>

        <nav className="mx-auto flex max-w-6xl gap-1 px-4">
          {TABS.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`border-b-2 px-3 py-2 text-sm font-medium transition ${
                tab === t
                  ? "border-indigo-600 text-indigo-700"
                  : "border-transparent text-slate-500 hover:text-slate-700"
              }`}
            >
              {t}
            </button>
          ))}
        </nav>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-5">
        {tab === "Assistant" ? (
          <div className="h-[calc(100vh-185px)] overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
            <ChatPanel role={role} manager={manager} provider={provider} />
          </div>
        ) : tab === "Dashboard" ? (
          <Dashboard
            role={role}
            manager={manager}
            onSelect={setSelected}
            goToReminders={() => setTab("Reminders")}
          />
        ) : tab === "People" ? (
          <PeoplePanel role={role} manager={manager} onSelect={setSelected} />
        ) : tab === "Reminders" ? (
          <RemindersPanel role={role} manager={manager} onSelect={setSelected} />
        ) : (
          <ProgressionPanel role={role} manager={manager} onSelect={setSelected} />
        )}
      </main>

      <ProfileDrawer associateId={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
