// The workspace talks to the FastAPI backend. In dev, vite proxies these paths to :8000.
// For a static build served elsewhere, set VITE_API_BASE.
const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "";

async function jf<T>(path: string, opts?: RequestInit): Promise<T> {
  const r = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!r.ok) throw new Error((await r.text()) || r.statusText);
  return r.json();
}

export type Vars = Record<string, unknown> & { format?: string; mode?: string };

export const api = {
  brief: (brief: string, action = "plan", image_urls: string[] = []) =>
    jf<any>("/brief", { method: "POST", body: JSON.stringify({ brief, action, image_urls }) }),
  preview: (variables: Vars) =>
    jf<any>("/prompt", { method: "POST", body: JSON.stringify(variables) }),
  generate: (variables: Vars, image_urls: string[], auto_evaluate = true, prompt_override?: string) =>
    jf<any>("/generate", {
      method: "POST",
      body: JSON.stringify({ variables, image_urls, auto_evaluate, prompt_override }),
    }),
  refine: (variables: Vars, image_urls: string[]) =>
    jf<any>("/refine", { method: "POST", body: JSON.stringify({ variables, image_urls }) }),
  series: (variables: Vars, image_urls: string[], count: number) =>
    jf<any>("/series", { method: "POST", body: JSON.stringify({ variables, image_urls, count }) }),
  rate: (generation_id: string, human_score: number) =>
    jf<any>("/rate", { method: "POST", body: JSON.stringify({ generation_id, human_score }) }),
  generations: () => jf<any[]>("/generations"),
  leaderboard: () => jf<Record<string, any[]>>("/leaderboard"),
  patterns: () => jf<any>("/patterns"),
  usage: () => jf<any>("/usage"),
  variant: (action: "add" | "edit" | "delete", slot: string, text?: string, id?: string) =>
    jf<any>("/variant", { method: "POST", body: JSON.stringify({ action, slot, text, id }) }),
};

export function fileToDataURL(f: File): Promise<string> {
  return new Promise((res, rej) => {
    const r = new FileReader();
    r.onload = () => res(r.result as string);
    r.onerror = rej;
    r.readAsDataURL(f);
  });
}
