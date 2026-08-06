import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { Button, Card, CardContent, CardHeader, CardTitle, Badge } from "../components/ui";
import { api } from "../lib/api";
import { round } from "../lib/utils";

export default function Usage() {
  const [u, setU] = useState<any>(null);
  async function load() { setU(await api.usage()); }
  useEffect(() => { load(); }, []);
  if (!u) return <p className="text-muted">Načítám…</p>;

  const trend = u.score_trend || [];
  const max = 100;

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center gap-2">
        <h2 className="text-sm font-semibold">Usage & kredity</h2>
        <Button size="sm" variant="ghost" onClick={load}><RefreshCw className="h-3.5 w-3.5" /> Obnovit</Button>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label="Generací" value={u.generations} />
        <Stat label="Ohodnoceno tebou" value={u.rated} />
        <Stat label="Průměrné skóre" value={round(u.avg_score)} />
        <Stat label="Odhad nákladů" value={`$${u.est_cost_usd}`} sub="rough est." />
      </div>

      <Card>
        <CardHeader><CardTitle>Skóre v čase (posledních {trend.length})</CardTitle></CardHeader>
        <CardContent>
          {trend.length === 0 ? <p className="text-xs text-dim">Zatím žádná data.</p> : (
            <div className="flex h-40 items-end gap-1">
              {trend.map((t: any, i: number) => (
                <div key={i} title={`${round(t.score)}`}
                  className="flex-1 rounded-t bg-gradient-to-t from-forest to-bright"
                  style={{ height: `${Math.max(4, ((t.score || 0) / max) * 100)}%` }} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Breakdown title="Podle módu" data={u.by_mode} />
        <Breakdown title="Podle formátu" data={u.by_format} />
      </div>
      <p className="text-xs text-dim">
        Náklady jsou odhad z logu generací (config COST_IMAGE / COST_IMAGE_TEXT / COST_CRITIQUE).
        Reálný zůstatek kreditu zjistíš na replicate.com a console.anthropic.com.
      </p>
    </div>
  );
}

function Stat({ label, value, sub }: { label: string; value: any; sub?: string }) {
  return (
    <Card>
      <CardContent>
        <div className="text-xs text-dim">{label}</div>
        <div className="text-3xl font-extrabold">{value}</div>
        {sub && <div className="text-[11px] text-dim">{sub}</div>}
      </CardContent>
    </Card>
  );
}

function Breakdown({ title, data }: { title: string; data: Record<string, number> }) {
  const entries = Object.entries(data || {}).sort((a, b) => b[1] - a[1]);
  return (
    <Card>
      <CardHeader><CardTitle>{title}</CardTitle></CardHeader>
      <CardContent className="flex flex-col gap-1">
        {entries.length === 0 ? <p className="text-xs text-dim">—</p> :
          entries.map(([k, n]) => (
            <div key={k} className="flex items-center justify-between text-sm">
              <span className="text-muted">{k}</span><Badge tone="muted">{n}×</Badge>
            </div>
          ))}
      </CardContent>
    </Card>
  );
}
