"use client";

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import type { ChatTurn, Role } from "@/lib/types";
import { Markdown } from "./Markdown";

interface Props {
  role: Role;
  manager: string;
  provider: string;
}

const SUGGESTIONS: Record<Role, string[]> = {
  "TD Manager": [
    "Which associates have competencies or certifications expiring in the next 90 days?",
    "Who is ready for promotion and who has gaps?",
    "Give me an org-wide talent development summary.",
    "Recommend nominations for the Applied GenAI program.",
  ],
  "Project Manager": [
    "Summarise my team's learning hours and competency coverage.",
    "Which of my team members have expiring certifications?",
    "Who on my team is ready for career progression?",
    "Suggest TD program nominations for my team based on skill gaps.",
  ],
};

export function ChatPanel({ role, manager, provider }: Props) {
  const [messages, setMessages] = useState<ChatTurn[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [tools, setTools] = useState<string[]>([]);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(text: string) {
    const q = text.trim();
    if (!q || loading) return;
    const next = [...messages, { role: "user" as const, content: q }];
    setMessages(next);
    setInput("");
    setLoading(true);
    setTools([]);
    try {
      const context: ChatTurn = {
        role: "user",
        content:
          `Context: I am ${manager}, acting as a ${role}.` +
          (role === "Project Manager"
            ? ` When relevant, scope answers to my team (associates whose project or TD manager is ${manager}).`
            : ` I have an org-wide view across all teams.`),
      };
      const res = await api.chat([context, ...next]);
      setMessages([...next, { role: "assistant", content: res.answer }]);
      setTools(res.tool_calls.map((t) => t.name));
    } catch {
      setMessages([
        ...next,
        {
          role: "assistant",
          content:
            "⚠️ Something went wrong reaching the assistant. Make sure the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto px-1 py-2">
        {messages.length === 0 && (
          <div className="mx-auto max-w-2xl pt-6 text-center">
            <h2 className="text-lg font-semibold text-slate-800">
              Ask TD Compass anything about your people
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Consolidated learning hours, certifications, E1/E2 competencies, TD
              programs and HR policies — with AI recommendations.
            </p>
            <div className="mt-5 grid gap-2 sm:grid-cols-2">
              {SUGGESTIONS[role].map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-lg border border-slate-200 bg-white p-3 text-left text-sm text-slate-700 shadow-sm transition hover:border-indigo-300 hover:bg-indigo-50"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 shadow-sm ${
                m.role === "user"
                  ? "bg-indigo-600 text-white"
                  : "border border-slate-200 bg-white text-slate-800"
              }`}
            >
              {m.role === "user" ? (
                <span className="text-sm">{m.content}</span>
              ) : (
                <Markdown>{m.content}</Markdown>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
              <span className="inline-flex gap-1">
                <span className="animate-bounce">●</span>
                <span className="animate-bounce [animation-delay:0.15s]">●</span>
                <span className="animate-bounce [animation-delay:0.3s]">●</span>
              </span>
            </div>
          </div>
        )}
        {tools.length > 0 && !loading && (
          <div className="text-center text-xs text-slate-400">
            Sources queried: {tools.join(", ")}
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="border-t border-slate-200 bg-white p-3">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send(input);
              }
            }}
            rows={1}
            placeholder={`Ask as ${manager} (${role})…`}
            className="max-h-32 flex-1 resize-none rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
          />
          <button
            onClick={() => send(input)}
            disabled={loading || !input.trim()}
            className="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:opacity-40"
          >
            Send
          </button>
        </div>
        <div className="mt-1.5 text-center text-[11px] text-slate-400">
          {provider === "rule-based"
            ? "Running in offline rule-based mode — add an LLM API key for full conversational intelligence."
            : `Powered by ${provider} · responses use live dummy talent data`}
        </div>
      </div>
    </div>
  );
}
