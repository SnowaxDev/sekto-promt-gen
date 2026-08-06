import { useEffect, useRef, useState } from "react";
import { Radio } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, Badge } from "../components/ui";
import { api } from "../lib/api";
import { round } from "../lib/utils";

export default function Activity() {
  const [gens, setGens] = useState<any[]>([]);
  const [live, setLive] = useState(true);
  const timer = useRef<number | null>(null);

  async function load() {
    try {
      const g = await api.generations();
      setGens([...g].sort((a, b) => (b.ts || 0) - (a.ts || 0)));
    } catch { /* backend may be down briefly */ }
  }
  useEffect(() => {
    load();
    if (live) timer.current = window.setInterval(load, 4000);
    return () => { if (timer.current) window.clearInterval(timer.current); };
  }, [live]);

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center gap-2">
        <h2 className="text-sm font-semibold">Živá aktivita</h2>
        <button onClick={() => setLive((v) => !v)}
          className="inline-flex items-center gap-1 rounded-full border border-line px-2 py-0.5 text-xs text-muted">
          <Radio className={"h-3 w-3 " + (live ? "text-bright" : "text-dim")} /> {live ? "LIVE (4s)" : "pozastaveno"}
        </button>
        <span className="text-xs text-dim">{gens.length} generací</span>
      </div>

      <Card>
        <CardHeader><CardTitle>Poslední generace</CardTitle></CardHeader>
        <CardContent className="flex flex-col divide-y divide-line">
          {gens.length === 0 && <p className="text-xs text-dim">Zatím žádná aktivita.</p>}
          {gens.slice(0, 60).map((g) => (
            <div key={g._id} className="flex items-center gap-3 py-2">
              {g.output_url && <img src={g.output_url} className="h-12 w-12 rounded-lg object-cover border border-line" />}
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-1 text-xs">
                  <Badge tone="muted">{g.format}</Badge>
                  <Badge tone="muted">{g.mode}</Badge>
                  {g.series_id && <Badge tone="ok">série #{g.slide_index}</Badge>}
                  {g.hard_fail && <Badge tone="bad">⛔ hard fail</Badge>}
                  {g.human_score != null && <Badge tone="gold">★ {round(g.human_score)}</Badge>}
                </div>
                {g.auto_defects?.length > 0 && (
                  <div className="truncate text-[11px] text-dim">{g.auto_defects.join(", ")}</div>
                )}
                <div className="text-[11px] text-dim">{ago(g.ts)}</div>
              </div>
              <div className="text-2xl font-extrabold">{round(g.final_score)}</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function ago(ts?: number) {
  if (!ts) return "";
  const s = Math.max(0, Math.floor(Date.now() / 1000 - ts));
  if (s < 60) return `před ${s}s`;
  if (s < 3600) return `před ${Math.floor(s / 60)} min`;
  if (s < 86400) return `před ${Math.floor(s / 3600)} h`;
  return `před ${Math.floor(s / 86400)} dny`;
}
