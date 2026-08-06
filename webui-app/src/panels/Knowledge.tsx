import { useEffect, useState } from "react";
import { Plus, Save, Trash2, RefreshCw } from "lucide-react";
import { Button, Card, CardContent, CardHeader, CardTitle, Textarea, Badge } from "../components/ui";
import { api } from "../lib/api";

export default function Knowledge() {
  const [data, setData] = useState<any>(null);
  const [board, setBoard] = useState<Record<string, any[]>>({});
  const [status, setStatus] = useState("");

  async function load() {
    setData(await api.patterns());
    setBoard(await api.leaderboard());
  }
  useEffect(() => { load(); }, []);

  function meanOf(slot: string, id: string) {
    const row = (board[slot] || []).find((v) => v.id === id);
    return row ? { mean: row.mean, uses: row.uses } : { mean: 60, uses: 0 };
  }

  async function act(fn: () => Promise<any>, msg: string) {
    try { await fn(); await load(); setStatus(msg); }
    catch (e: any) { setStatus("Chyba: " + (e?.message || e)); }
  }

  if (!data) return <p className="text-muted">Načítám knowledge…</p>;

  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1fr_360px]">
      <div className="flex flex-col gap-5">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold">Živá knowledge DB — varianty promptů</h2>
          <Button size="sm" variant="ghost" onClick={load}><RefreshCw className="h-3.5 w-3.5" /> Obnovit</Button>
          {status && <span className="text-xs text-muted">{status}</span>}
        </div>
        {Object.entries(data.variants).map(([slot, variants]: [string, any]) => (
          <Card key={slot}>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>
                {slot} {slot.startsWith("de_") && <Badge tone="ok" className="ml-1">styl-osa</Badge>}
              </CardTitle>
              <AddVariant onAdd={(text) => act(() => api.variant("add", slot, text), "Přidáno.")} />
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              {variants.map((v: any) => (
                <VariantRow key={v.id} slot={slot} v={v} stat={meanOf(slot, v.id)}
                  onSave={(text) => act(() => api.variant("edit", slot, text, v.id), "Uloženo.")}
                  onDelete={() => act(() => api.variant("delete", slot, undefined, v.id), "Smazáno.")} />
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="flex flex-col gap-5">
        <Card>
          <CardHeader><CardTitle>Failure log ({data.failure_log.length})</CardTitle></CardHeader>
          <CardContent className="flex flex-col gap-2">
            {data.failure_log.map((f: any) => (
              <div key={f.id} className="text-xs text-muted">
                <b className="text-ink">{f.id}</b> — {f.symptom} <span className="text-dim">→ {f.fix}</span>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Negative prompt ({data.base_negative.length})</CardTitle></CardHeader>
          <CardContent><p className="text-xs text-dim">{data.base_negative.join(", ")}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Copy banky (Dark Emerald)</CardTitle></CardHeader>
          <CardContent className="flex flex-col gap-2">
            {Object.entries(data.banks || {}).map(([k, arr]: [string, any]) => (
              <div key={k} className="text-xs">
                <b>{k}</b>: <span className="text-muted">{(Array.isArray(arr) ? arr.map((x: any) => Array.isArray(x) ? x.join(" ") : x) : []).join(" · ")}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function VariantRow({ v, stat, onSave, onDelete }: {
  slot: string; v: any; stat: { mean: number; uses: number };
  onSave: (t: string) => void; onDelete: () => void;
}) {
  const [text, setText] = useState(v.text);
  const dirty = text !== v.text;
  return (
    <div className="rounded-xl border border-line bg-void/30 p-3">
      <div className="mb-2 flex items-center gap-2 text-xs">
        <span className="font-mono text-dim">{v.id}</span>
        <Badge tone={stat.mean >= 80 ? "ok" : "muted"}>⌀ {stat.mean}</Badge>
        <Badge tone="muted">{stat.uses}× použito</Badge>
        <div className="ml-auto flex gap-1">
          <Button size="sm" variant="ghost" disabled={!dirty} onClick={() => onSave(text)}><Save className="h-3.5 w-3.5" /> Uložit</Button>
          <Button size="sm" variant="danger" onClick={onDelete}><Trash2 className="h-3.5 w-3.5" /></Button>
        </div>
      </div>
      <Textarea rows={2} value={text} onChange={(e) => setText(e.target.value)} />
    </div>
  );
}

function AddVariant({ onAdd }: { onAdd: (t: string) => void }) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  if (!open) return <Button size="sm" variant="ghost" onClick={() => setOpen(true)}><Plus className="h-3.5 w-3.5" /> Přidat</Button>;
  return (
    <div className="flex w-full max-w-md items-center gap-2">
      <Textarea rows={1} value={text} onChange={(e) => setText(e.target.value)} placeholder="text nové varianty…" />
      <Button size="sm" onClick={() => { onAdd(text); setText(""); setOpen(false); }}>OK</Button>
    </div>
  );
}
