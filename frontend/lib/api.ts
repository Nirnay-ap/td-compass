import type {
  Associate,
  ChatTurn,
  OrgSummary,
  ProgressionCandidate,
  ReminderItem,
} from "./types";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`/api/${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const api = {
  health: () => get<{ status: string; llm_provider: string }>("health"),
  summary: () => get<OrgSummary>("summary"),
  managers: () =>
    get<{ project_managers: string[]; td_managers: string[] }>("managers"),
  associates: (manager?: string) =>
    get<{ count: number; associates: Associate[] }>(
      "associates" + (manager ? `?manager=${encodeURIComponent(manager)}` : ""),
    ),
  associate: (id: string) => get<Associate>(`associates/${id}`),
  reminders: (manager?: string, withinDays = 90) =>
    get<{ count: number; expired: ReminderItem[]; expiring_soon: ReminderItem[] }>(
      `reminders?within_days=${withinDays}` +
        (manager ? `&manager=${encodeURIComponent(manager)}` : ""),
    ),
  progression: (manager?: string, onlyReady = false) =>
    get<{ count: number; candidates: ProgressionCandidate[] }>(
      `progression?only_ready=${onlyReady}` +
        (manager ? `&manager=${encodeURIComponent(manager)}` : ""),
    ),
  chat: async (messages: ChatTurn[]) => {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
    });
    if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
    return res.json() as Promise<{
      answer: string;
      tool_calls: { name: string; args: Record<string, unknown> }[];
      provider: string;
    }>;
  },
};
