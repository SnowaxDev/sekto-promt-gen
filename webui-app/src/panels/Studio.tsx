import { useState } from "react";
import { Wand2, Eye, Play, Sparkles, Film, Upload, Copy } from "lucide-react";
import {
  Button, Card, CardContent, CardHeader, CardTitle, Input, Textarea, Select, Label, Badge,
} from "../components/ui";
import { api, fileToDataURL, type Vars } from "../lib/api";
import { round } from "../lib/utils";

const FORMATS = [
  { g: "Dark Emerald (digital)", opts: ["ig_post", "ig_portrait", "story", "og_banner"] },
  { g: "Tisk / letáky", opts: ["DL", "A5", "A4", "A3", "banner_vertical", "banner_horizontal", "rollup", "social"] },
];
const MODES = [
  ["dark_emerald", "Dark Emerald v3 (pro digital)"],
  ["B_sluzby", "B — Služby (diagonála)"],
  ["A_transformace", "A — Transformace (před/po)"],
  ["editorial_immersive", "Editorial Immersive (reálné foto)"],
];

export default function Studio() {
  const [brief, setBrief] = useState("");
  const [format, setFormat] = useState("ig_post");
  const [mode, setMode] = useState("dark_emerald");
  const [headline, setHeadline] = useState("");
  const [ladder, setLadder] = useState("");
  const [chips, setChips] = useState("");
  const [location, setLocation] = useState("Dvůr Králové a okolí");
  const [files, setFiles] = useState<File[]>([]);
  const [styleRef, setStyleRef] = useState(false);
  const [count, setCount] = useState(4);
  const [prompt, setPrompt] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [series, setSeries] = useState<any>(null);

  function vars(): Vars {
    const v: Vars = { format, mode, location };
    if (headline.trim()) v.service_headline = headline.trim();
    if (styleRef) (v as any).style_ref = true;
    if (mode === "dark_emerald") {
      const l = ladder.split(",").map((s) => s.trim()).filter(Boolean);
      if (l.length) (v as any).ladder = l;
      const c = chips.split(",").map((s) => s.trim()).filter(Boolean);
      if (c.length) (v as any).chips = c;
    }
    return v;
  }
  async function imgs() {
    return Promise.all(files.map(fileToDataURL));
  }

  function applyPlan(v: any) {
    if (!v) return;
    if (v.format) setFormat(v.format);
    if (v.mode) setMode(v.mode);
    if (v.location) setLocation(v.location);
    if (v.service_headline) setHeadline(v.service_headline);
    if (v.ladder) setLadder((v.ladder || []).join(", "));
    if (v.chips) setChips((v.chips || []).join(", "));
    if (v.count) setCount(v.count);
  }

  async function guard(fn: () => Promise<void>, msg: string) {
    setBusy(true);
    setStatus(msg);
    try {
      await fn();
    } catch (e: any) {
      setStatus("Chyba: " + (e?.message || e));
    } finally {
      setBusy(false);
    }
  }

  const plan = () =>
    guard(async () => {
      const d = await api.brief(brief, "plan");
      applyPlan(d.variables);
      setPrompt(d.prompt);
      setResult(null);
      setSeries(null);
      setStatus(`Naplánováno ✓ ${d.variables.mode} · ${d.variables.format}` + (d.variables.series ? ` · série ${d.variables.count}×` : ""));
    }, "🧠 Plánuji z popisu…");

  const preview = () =>
    guard(async () => {
      const d = await api.preview(vars());
      setPrompt(d.prompt);
      setStatus("Prompt hotov (náklad 0).");
    }, "Sestavuji prompt…");

  const generate = () =>
    guard(async () => {
      const g = await api.generate(vars(), await imgs(), true, prompt || undefined);
      setResult(g);
      setSeries(null);
      setStatus("Hotovo.");
    }, "Generuji na Replicate… (~30–60 s)");

  const refine = () =>
    guard(async () => {
      const d = await api.refine(vars(), await imgs());
      setResult(d.best);
      (d.best as any)._history = d.history;
      (d.best as any)._discovered = d.discovered;
      setSeries(null);
      setStatus(`Vylepšeno — nejlepší z ${d.iterations} verzí.`);
    }, "✨ Vylepšuji automaticky (až 3×)…");

  const makeSeries = () =>
    guard(async () => {
      const d = await api.series(vars(), await imgs(), count);
      setSeries(d);
      setResult(null);
      setStatus(`Série hotová — ${d.count} příspěvků, jednotný styl.`);
    }, `🎞️ Generuji sérii ${count}×…`);

  async function rate(id: string, score: number) {
    await api.rate(id, score);
    setStatus("Hodnocení uloženo — varianty přebodovány.");
  }

  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-[380px_1fr]">
      {/* LEFT: builder */}
      <Card>
        <CardHeader><CardTitle>Vytvořit materiál</CardTitle></CardHeader>
        <CardContent>
          <Label>🧠 Napiš, co chceš — systém to naplánuje z knowledge</Label>
          <Textarea rows={2} value={brief} onChange={(e) => setBrief(e.target.value)}
            placeholder="nábor story do týmu s důrazem na kácení · A3 plakát na sekání · carousel o údržbě" />
          <Button className="mt-2 w-full" disabled={busy} onClick={plan}><Wand2 className="h-4 w-4" /> Naplánuj z popisu</Button>

          <Label>Formát</Label>
          <Select value={format} onChange={(e) => setFormat(e.target.value)}>
            {FORMATS.map((grp) => (
              <optgroup key={grp.g} label={grp.g}>
                {grp.opts.map((o) => <option key={o} value={o}>{o}</option>)}
              </optgroup>
            ))}
          </Select>

          <Label>Styl (mód)</Label>
          <Select value={mode} onChange={(e) => setMode(e.target.value)}>
            {MODES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </Select>

          <Label>Headline / služba (volitelné)</Label>
          <Input value={headline} onChange={(e) => setHeadline(e.target.value)} placeholder="Sekáme. Kácíme. Čistíme." />

          {mode === "dark_emerald" && (
            <>
              <Label>Headline ladder — 3 řádky (čárkou)</Label>
              <Input value={ladder} onChange={(e) => setLadder(e.target.value)} placeholder="ZAHRADA, NA KTERÉ, ZÁLEŽÍ." />
              <Label>Chipy služeb — 2–4 (čárkou)</Label>
              <Input value={chips} onChange={(e) => setChips(e.target.value)} placeholder="Sekání trávy, Kácení stromů, Střih keřů a tújí" />
            </>
          )}

          <Label>Lokalita</Label>
          <Input value={location} onChange={(e) => setLocation(e.target.value)} />

          <Label>Reference / styl — nahraj z PC</Label>
          <label className="flex cursor-pointer items-center gap-2 rounded-xl border border-line bg-void/40 px-3 py-2 text-sm text-muted hover:bg-white/[0.05]">
            <Upload className="h-4 w-4" />
            <span>{files.length ? `${files.length} souborů` : "Vybrat obrázky…"}</span>
            <input type="file" accept="image/*" multiple className="hidden"
              onChange={(e) => setFiles(Array.from(e.target.files || []))} />
          </label>
          <label className="mt-2 flex items-center gap-2 text-xs text-muted">
            <input type="checkbox" checked={styleRef} onChange={(e) => setStyleRef(e.target.checked)} />
            Poslední obrázek je stylová reference
          </label>

          <div className="mt-3 grid grid-cols-2 gap-2">
            <Button variant="ghost" disabled={busy} onClick={preview}><Eye className="h-4 w-4" /> Náhled</Button>
            <Button disabled={busy} onClick={generate}><Play className="h-4 w-4" /> Vygenerovat</Button>
          </div>
          <Button variant="subtle" className="mt-2 w-full" disabled={busy} onClick={refine}>
            <Sparkles className="h-4 w-4" /> Vylepšit automaticky (max 3×)
          </Button>
          <div className="mt-2 flex items-center gap-2">
            <Input type="number" min={1} max={8} value={count} className="w-20"
              onChange={(e) => setCount(parseInt(e.target.value) || 3)} />
            <Button variant="ghost" className="flex-1" disabled={busy} onClick={makeSeries}>
              <Film className="h-4 w-4" /> Vygenerovat sérii
            </Button>
          </div>
          {status && <p className="mt-3 text-xs text-muted">{status}</p>}
        </CardContent>
      </Card>

      {/* RIGHT: prompt (editable) + result */}
      <div className="flex flex-col gap-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Sestavený prompt (editovatelný)</CardTitle>
            <Button size="sm" variant="ghost" onClick={() => navigator.clipboard.writeText(prompt)}>
              <Copy className="h-3.5 w-3.5" /> Kopírovat
            </Button>
          </CardHeader>
          <CardContent>
            <Textarea rows={12} value={prompt} onChange={(e) => setPrompt(e.target.value)}
              placeholder="Klikni Naplánuj / Náhled — nebo napiš prompt ručně. Uprav a dej Vygenerovat, pošle se tvoje verze." />
            <p className="mt-2 text-xs text-dim">Úprava se použije při „Vygenerovat" (pošle se tvůj upravený prompt).</p>
          </CardContent>
        </Card>

        {result && <ResultCard g={result} onRate={rate} />}
        {series && <SeriesCard d={series} onRate={rate} />}
      </div>
    </div>
  );
}

function ResultCard({ g, onRate }: { g: any; onRate: (id: string, s: number) => void }) {
  const [hs, setHs] = useState(Math.round(g.final_score || 70));
  const checks = g.auto_checks || {};
  return (
    <Card>
      <CardHeader><CardTitle>Výsledek</CardTitle></CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-4">
          {g.output_url && <img src={g.output_url} className="w-64 rounded-xl border border-line" />}
          <div className="min-w-[240px] flex-1">
            <div className="text-3xl font-extrabold">{round(g.final_score)} <span className="text-sm text-dim">/100</span></div>
            {g.hard_fail
              ? <Badge tone="bad" className="my-1">⛔ HARD FAIL — nepublikovat</Badge>
              : g.final_score >= 92 && <Badge tone="ok" className="my-1">★ baseline kvalita</Badge>}
            <p className="text-xs text-dim">auto: {round(g.auto_score)} · id: {g._id}</p>
            <div className="my-2 flex flex-wrap gap-1">
              {Object.entries(checks).map(([k, v]) => (
                <Badge key={k} tone={v ? "ok" : "bad"}>{v ? "✓" : "✗"} {k}</Badge>
              ))}
            </div>
            {g.auto_defects?.length > 0 && <p className="text-xs text-muted">Vady: {g.auto_defects.join(", ")}</p>}
            {g._discovered && <p className="mt-1 text-xs text-blade">🧪 Nový styl objeven ({g._discovered.axis}): {g._discovered.text}</p>}
            <div className="mt-3 flex items-center gap-2">
              <Input type="number" min={0} max={100} value={hs} className="w-24"
                onChange={(e) => setHs(parseInt(e.target.value) || 0)} />
              <Button size="sm" onClick={() => onRate(g._id, hs)}>Uložit hodnocení</Button>
            </div>
          </div>
        </div>
        {g._history && (
          <div className="mt-4 border-t border-line pt-3">
            <div className="mb-1 text-xs font-semibold">Průběh vylepšování</div>
            {g._history.map((h: any) => (
              <div key={h.iter} className="text-xs text-muted">
                #{h.iter} — skóre <b className="text-ink">{round(h.score)}</b>{" "}
                {h.hard_fail ? "· ⛔" : h.defects?.length ? "· " + h.defects.join(", ") : "· bez vad"}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function SeriesCard({ d, onRate }: { d: any; onRate: (id: string, s: number) => void }) {
  return (
    <Card>
      <CardHeader><CardTitle>Série {d.series_id} — {d.count} příspěvků (jednotný styl)</CardTitle></CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {d.slides.map((s: any) => (
            <div key={s.slide} className="overflow-hidden rounded-xl border border-line bg-void/40">
              {s.output_url && <img src={s.output_url} className="h-40 w-full object-cover" />}
              <div className="p-2 text-xs">
                <b>#{s.slide}</b> <span className="text-dim">{s.role}</span>
                <div className="mt-1 flex items-center justify-between">
                  <span className="text-lg font-bold">{round(s.score)}</span>
                  <Button size="sm" variant="ghost" onClick={() => onRate(s.id, 85)}>Ohodnotit</Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
