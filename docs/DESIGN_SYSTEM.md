# SeknuTo.cz — MASTER DESIGN & BRAND IDENTITY SYSTEM
## „DARK EMERALD" v3.0 — reprodukovatelný, strojově čitelný, self-improving

> **Co to je:** Jediný autoritativní zdroj pravdy pro veškerý vizuální output SeknuTo.cz.
> Nahrazuje `references/design-system.md` (v1) a povyšuje `seknuto-prompts` z „prompt kuchařky" na **design systém**.
>
> **Proč vznikl:** Výstupy z června–srpna 2026 (dark emerald IG posty, OG banner, kalkulace post, nábor story, DL leták s diagonálou, kácení kampaň) dosáhly kvality, kterou je potřeba **zamknout a reprodukovat**, ne znovu vymýšlet. Tento soubor je destilace toho, co v nich funguje — rozložená na tokeny, komponenty, chassis a pravidla.
>
> **Jak se používá:** Claude načte tento soubor PŘED tvorbou jakéhokoliv vizuálu. Vybere formát → načte chassis → vyplní tokeny → vygeneruje prompt → oskóruje rubrikou → případně iteruje. Bez lidského dolaďování.
>
> **Verze:** v3.0 · **Platí od:** srpen 2026 · **Maintainer:** Dušan Macháček + Claude

---

## 📑 OBSAH

| # | Sekce | Kdy číst |
|---|-------|----------|
| 1 | [Pozicování & designová teze](#1) | vždy — určuje tón |
| 2 | [Design tokeny (strojově čitelné)](#2) | vždy |
| 3 | [Canvas systém — 5 vrstev pozadí](#3) | každý digitální asset |
| 4 | [Typografický systém](#4) | vždy |
| 5 | [Komponentní knihovna (14 komponent)](#5) | vždy |
| 6 | [Layout chassis — 5 zón + reflow](#6) | vždy |
| 7 | [Fotografie & brand human](#7) | asset s fotkou |
| 8 | [Formátová matice](#8) | výběr formátu |
| 9 | [Copy systém & textové banky](#9) | vždy |
| 10 | [Česká diakritika — enforcement](#10) | vždy |
| 11 | [Master prompt generátor](#11) | tvorba promptu |
| 12 | [Negative prompt (LOCKED)](#12) | tvorba promptu |
| 13 | [QA rubrika 0–100](#13) | po výstupu |
| 14 | [Napojení na seknuto-forge](#14) | automatizace |
| 15 | [Evoluce — LOCKED vs. VARIABLE](#15) | před změnou systému |
| 16 | [Failure log v3](#16) | před promptem |
| 17 | [Pre-flight checklist](#17) | před odesláním |

---

<a id="1"></a>
## 1. POZICOVÁNÍ & DESIGNOVÁ TEZE

### 1.1 Jednovětá teze

> **SeknuTo.cz vypadá jako prémiový technologický produkt, který dělá zahradnickou práci.**

Ne jako místní řemeslník s letáčkem z Wordu. Ne jako korporátní zahradnická firma s bílým pozadím a clipartem. **Tmavý smaragdový povrch, skleněné komponenty, chirurgická typografie, jedna zářící akce.** Estetika finanční appky přenesená do oboru, kde ji nikdo nečeká — a přesně proto funguje.

### 1.2 Proč dark emerald vyhrál

| Konkurence v regionu | SeknuTo.cz v3 |
|---|---|
| Bílé pozadí, zelený clipart | Tmavý smaragd s objemovým světlem |
| Cena hned na letáku | „Cena na míru · Kalkulace zdarma" |
| Stock fotka trávníku | Reálný tým, zlatá hodina, rim light |
| Telefon malým písmem dole | Telefon = druhý největší prvek na plátně |
| 12 služeb v seznamu | 3–4 chipy, jedna dominantní akce |
| Náhodný layout pokaždé | Jeden chassis, 5 zón, reflow dle poměru |

**Výsledek:** materiál je rozpoznatelný na 2 metry a na 200 ms. To je jediná metrika, která rozhoduje.

### 1.3 Tři nepřekročitelné principy

1. **Konzistence poráží kreativitu.** 10× stejný chassis > 10 chytrých konceptů. Brand se staví opakováním.
2. **Jedno plátno = jedna akce.** Vždy existuje právě jeden zářící zelený CTA. Vše ostatní k němu vede.
3. **Ticho je součást luxusu.** Minimálně 35 % plochy bez obsahu. Nacpaný design čte trh jako levný.

### 1.4 Emocionální rejstřík

| Chceme, aby divák cítil | Nechceme |
|---|---|
| „Tihle vědí, co dělají." | „Tihle jsou levní." |
| „Vypadá to draze, ale dostupně." | „Vypadá to jako reklama." |
| „Vyřeší to za mě celé." | „Budu to muset hlídat." |
| „Mladí, ale profesionální." | „Brigádníci." |

---

<a id="2"></a>
## 2. DESIGN TOKENY (strojově čitelné)

> Tento blok je zdroj pravdy pro CSS, React, docx generátory i AI prompty. Nikdy nepiš „zelená" — vždy token nebo hex.

```json
{
  "seknuto_tokens": {
    "version": "3.0",

    "color": {
      "canvas": {
        "void":        "#060D09",
        "emerald_900": "#0A1F14",
        "emerald_800": "#0F2C1C",
        "emerald_700": "#143823",
        "emerald_600": "#17422A",
        "charcoal":    "#1a1a1a"
      },
      "brand": {
        "green_700_forest": "#1E5A32",
        "green_600_dark":   "#2d8840",
        "green_500_primary":"#3FA34D",
        "green_400_bright": "#4FBF5E",
        "green_300_blade":  "#66BB6A",
        "green_200_light":  "#86D492"
      },
      "accent": {
        "yellow":   "#FFD54F",
        "star":     "#FFC93C",
        "red_before":"#D32F2F",
        "whatsapp": "#25D366"
      },
      "text": {
        "primary": "#FFFFFF",
        "muted":   "rgba(255,255,255,0.72)",
        "dim":     "rgba(255,255,255,0.45)",
        "ghost":   "rgba(255,255,255,0.30)",
        "on_light":"#1a1a1a",
        "gray":    "#666666"
      },
      "surface": {
        "panel":       "rgba(255,255,255,0.04)",
        "panel_raised":"rgba(255,255,255,0.07)",
        "glass":       "rgba(12,30,20,0.55)",
        "hairline":    "rgba(255,255,255,0.10)",
        "hairline_green":"rgba(63,163,77,0.35)",
        "grid":        "rgba(255,255,255,0.035)"
      }
    },

    "gradient": {
      "canvas_radial": "radial-gradient(120% 90% at 72% 8%, #17422A 0%, #0F2C1C 42%, #0A1F14 70%, #060D09 100%)",
      "cta_button":    "linear-gradient(135deg, #4FBF5E 0%, #3FA34D 45%, #2E8B41 100%)",
      "photo_fade":    "linear-gradient(90deg, rgba(10,31,20,1) 0%, rgba(10,31,20,0.75) 28%, rgba(10,31,20,0) 62%)",
      "bottom_scrim":  "linear-gradient(180deg, rgba(6,13,9,0) 0%, rgba(6,13,9,0.88) 65%, rgba(6,13,9,0.97) 100%)"
    },

    "glow": {
      "cta":   "0 0 64px rgba(63,163,77,0.45), 0 8px 28px rgba(0,0,0,0.45)",
      "badge": "0 0 22px rgba(63,163,77,0.55)",
      "dot":   "0 0 12px rgba(102,187,106,0.9)"
    },

    "radius": {
      "pill": 999,
      "card": 20,
      "panel": 16,
      "chip": 999,
      "cta": 22,
      "logo_plate": 18
    },

    "typography": {
      "display": { "family": "Montserrat", "weights": [800, 900], "case": "UPPERCASE", "tracking": "-0.02em", "leading": 0.86 },
      "headline": { "family": "Montserrat", "weights": [700, 800], "case": "Sentence", "tracking": "-0.01em", "leading": 1.02 },
      "body":    { "family": "Poppins", "weights": [400, 500, 600], "leading": 1.35 },
      "numeric": { "family": "Montserrat", "weights": [800], "note": "telefon, čísla, statistiky" },
      "eyebrow": { "family": "Poppins", "weight": 500, "case": "UPPERCASE", "tracking": "0.14em" }
    },

    "spacing_unit_pct_of_short_edge": {
      "xs": 1.2, "s": 2.2, "m": 3.6, "l": 5.5, "xl": 8.0
    },

    "layout": {
      "safe_margin_pct": 5.5,
      "story_ui_safe_top_pct": 9,
      "story_ui_safe_bottom_pct": 12,
      "min_empty_space_pct": 35,
      "max_text_blocks": 6
    }
  }
}
```

### 2.1 Pravidla barev — tvrdá

| Pravidlo | Důvod |
|---|---|
| **Žlutá `#FFD54F` maximálně 1× na plátno** | Je to jediný „přerušovač". Dvě žluté = žádná žlutá. |
| **Červená `#D32F2F` výhradně pro PŘED stav** | Nikdy jako akcent, nikdy v CTA. |
| **Nikdy nová zelená mimo paletu** | Šest odstínů stačí na vše. |
| **Text pod 14 px nikdy `text.dim`** | Nečitelnost = amatérismus. |
| **Bílá `#FFFFFF` jen na tmavém, `#1a1a1a` jen na světlém** | Žádná šedá na šedé. |

---

<a id="3"></a>
## 3. CANVAS SYSTÉM — 5 VRSTEV POZADÍ

> Toto je **jádro rozpoznatelnosti**. Každý digitální asset SeknuTo.cz staví přesně na těchto pěti vrstvách, v tomto pořadí. Nic se nevynechává.

```
VRSTVA 5  ▸ Corner brackets (rámečkové rohy)          ← nejvýš
VRSTVA 4  ▸ Vignette (ztmavení okrajů)
VRSTVA 3  ▸ Light shaft (objemový světelný kužel)
VRSTVA 2  ▸ Blueprint grid (technická mřížka)
VRSTVA 1  ▸ Emerald gradient base                      ← nejníž
```

### Vrstva 1 — Emerald gradient base
Radiální gradient, světelné centrum v pravém horním kvadrantu (72 % / 8 %).
`#17422A → #0F2C1C → #0A1F14 → #060D09`
Nikdy ploché jednobarevné pozadí. Nikdy černá bez zeleného nádechu.

### Vrstva 2 — Blueprint grid
Tenké linky `rgba(255,255,255,0.035)`, síla 1 px @1080.
Rozteč = 1/8 kratší hrany plátna. Jen mírně viditelná — **divák ji nemá vědomě zaregistrovat**, jen cítit „technickou přesnost".
U tiskových materiálů se vynechává (nevytiskne se čistě).

### Vrstva 3 — Light shaft
Jeden měkký objemový kužel z pravého horního rohu, úhel 30–40° dolů-doleva.
Barva `rgba(190,255,205,0.10)` → transparentní. Šířka ~28 % plátna.
Slouží k oddělení fotky od pozadí a k vytvoření hloubky. **Právě jeden kužel**, nikdy dva.

### Vrstva 4 — Vignette
Radiální ztmavení okrajů, střed 0 %, okraj 35 % `#060D09`. Drží pozornost uprostřed.

### Vrstva 5 — Corner brackets
Čtyři L-rohy, jen linky (žádná výplň):
- Síla: 3 px @1080 · Délka ramene: 7–9 % kratší hrany
- Odsazení od hrany: 3,5 % · Barva: `#3FA34D` při 65 % krytí
- Buď **všechny čtyři**, nebo žádný. Nikdy dva.

> **Když se vynechají corner brackets a grid**, materiál přestane být rozpoznatelný jako SeknuTo. Ověřeno na výstupech.

---

<a id="4"></a>
## 4. TYPOGRAFICKÝ SYSTÉM

### 4.1 Signature device: **Headline Ladder** (tříúrovňový žebřík)

Nejsilnější prvek celé identity. Headline se rozpadá do tří řádků se **stoupající intenzitou**:

```
Řádek 1  →  GHOST     rgba(255,255,255,0.30)   „ZAHRADA"      ← kontext, ustupuje
Řádek 2  →  WHITE     #FFFFFF                  „NA KTERÉ"     ← spojka, plná váha
Řádek 3  →  GREEN     #3FA34D                  „ZÁLEŽÍ."      ← pointa, brand barva
```

**Pravidla ladderu:**
- Montserrat 800/900, VERZÁLKY, tracking −2 %, leading 0,86 (řádky se skoro dotýkají)
- Tečka na konci třetího řádku **povinná** — uzavírá tvrzení
- 2 řádky = přípustné (ghost + green). 4 řádky = nikdy
- Ladder je vždy vlevo zarovnaný, nikdy na střed (výjimka: 4:5 kampaňové plakáty)
- Šířka bloku max 58 % plátna u 1:1 a 1.91:1

**Alternativní varianta: Outline + Solid** (viz „BEZPLATNÁ KALKULACE")
```
Řádek 1  →  OUTLINE   obrys 2px rgba(255,255,255,0.35), výplň žádná   „BEZPLATNÁ"
Řádek 2  →  SOLID     #3FA34D                                          „KALKULACE"
```
Používej, když je headline dvouslovný a druhé slovo je hodnota (KALKULACE, PROHLÍDKA, ÚDRŽBA).

### 4.2 Typografická škála (referenční plátno 1080 px)

| Role | Font / váha | Velikost @1080 | Barva |
|---|---|---|---|
| Display ladder | Montserrat 900 | 118–142 px | ghost / white / green |
| Display 2. úrovně | Montserrat 800 | 84–96 px | white |
| Eyebrow | Poppins 500, tracking 0.14em | 26–30 px | `green_200` / muted |
| Chip label | Poppins 600 | 27–30 px | white |
| Body / benefit | Poppins 600 | 34–38 px | white |
| Body sekundární | Poppins 400 | 30–33 px | muted |
| CTA text | Poppins 700 | 40–46 px | white |
| Telefon | Montserrat 800 | 52–64 px | white |
| Footer | Poppins 500 | 26–30 px | dim |
| Micro / disclaimer | Poppins 400 | 22–24 px | dim |

> **Škálování na jiný formát:** vynásob poměrem `kratší_hrana / 1080`. U tisku převáděj na body přes 300 DPI.

### 4.3 Zakázané typografické jevy

- ❌ Letter-spacing u českých slov v AI promptech (vzniká `V o l e j t e`)
- ❌ Více než 3 velikosti písma v jedné zóně
- ❌ Kurzíva u verzálek
- ❌ Stíny pod textem (místo toho scrim vrstva)
- ❌ Text přes fotku bez ztmavovacího scrimu
- ❌ Dělení slov (žádné pomlčky na konci řádků)

---

<a id="5"></a>
## 5. KOMPONENTNÍ KNIHOVNA

> 14 komponent. Každý asset se skládá **výhradně** z nich. Nová komponenta = nová verze systému (viz sekce 15).

### C1 — Brand Lockup (povinná, právě 1×)
Kruhový disk `#1E5A32` s bílými stébly + wordmark „SeknuTo.cz".
- Wordmark: Montserrat 700, bílá. Přípona „.cz" váha 500 (jemně odlišená)
- Volitelně v tmavém glass pillu `rgba(12,30,20,0.55)` + hairline border
- Pozice: levý horní roh (digital) / horní střed (story, plakát)
- **Logo se NIKDY nepřekresluje AI** — vždy jako image reference `/mnt/project/seknuto_cz.png`

### C2 — Status Pill (volitelná, max 1×)
Pilulka s pulzující zelenou tečkou + krátký text.
- bg `rgba(12,30,20,0.6)`, border `hairline`, radius pill
- Tečka: `#4FBF5E` 12 px + glow · Text: Poppins 600 bílá
- Bank: `Přijímáme objednávky` · `NÁBOR 2026` · `Volné termíny` · `Sezóna 2026`
- Pozice: pravý horní roh, vertikálně zarovnaná s lockupem

### C3 — Eyebrow Line
Jednořádkový kontext nad headlinem.
- `PROFESIONÁLNÍ PÉČE O ZAHRADU · Dvůr Králové a okolí`
- První část VERZÁLKY tracking 0.14em `green_200`, druhá část sentence case `muted`
- Oddělovač vždy `·` (middle dot), nikdy pomlčka ani svislítko

### C4 — Chip Row
2–4 outline pilulky se službami.
- Outline: border `hairline_green` 1,5 px, text bílá, bg `rgba(255,255,255,0.03)`
- **Právě jeden chip smí být filled** (`gradient.cta`) = zvýrazněná služba
- Volitelný mikro-tag „NOVÉ" (žlutý, malý) plovoucí nad jedním chipem — max 1× na plátno
- Nikdy více než 4 chipy

### C5 — Headline Ladder
Viz 4.1. Právě 1× na plátno.

### C6 — Accent Rule + Body
Svislá zelená linka `#3FA34D` (4 px) vlevo + 1–2 řádky textu.
Používá se pro výčet služeb nebo benefit větu pod headlinem.

### C7 — Glass Proof Card
Skleněná karta s důkazem.
- bg `glass`, backdrop blur 18 px, border `hairline_green`, radius 20
- Obsah: 5 hvězd `#FFC93C` + `20+ spokojených zákazníků` nebo `Hodnocení na Google`
- Pozice: pravá polovina, nikdy nepřekrývá obličej na fotce
- Právě 1× na plátno

### C8 — List Card (pro story / delší formáty)
Tmavý panel s kruhovou ikonou.
- Panel: bg `panel`, border `hairline_green`, radius 16, výška 11–13 % plátna
- Ikona: kruh `gradient.cta` průměr = 70 % výšky panelu, bílý glyph uvnitř
- Label: Poppins 700 bílá, vertikálně na střed
- 3 karty = optimum. 4 = maximum. 2 = vypadá nedodělaně

### C9 — Primary CTA Button (povinná, právě 1×)
- Šířka: 100 % obsahové šířky (digital) nebo 62 % (banner)
- Výška: 8,5–10 % výšky plátna · radius 22
- bg `gradient.cta` + `glow.cta` + horní vnitřní světlo `rgba(255,255,255,0.22)` 1 px
- Text: Poppins 700 bílá, vycentrovaný, volitelně ikona vlevo / šipka `→` vpravo
- **Toto je jediný zářící prvek na plátně.** Nic jiného nemá glow.

### C10 — Contact Footer
`SeknuTo.cz · 730 588 372` — Poppins 600 / Montserrat 800 pro číslo.
Zarovnání: vpravo (1:1, 4:5) nebo na střed (9:16, plakát).

### C11 — Micro CTA Line
Jednořádková nabídka nad hlavním CTA: `Pošli foto zahrady — nabídka ZDARMA 📸`
Emoji povoleno **jen na sociálních sítích**, nikdy na tisku.

### C12 — Diagonal Split (print / před-po)
Signature device pro tisk. Úhel **42–45°**, vzestupný zleva doprava.
- Hrana: bílá 6–10 px NEBO zelená `#3FA34D` — vždy jedna, nikdy obě
- Levá strana = PŘED (desaturace −25 %, chladnější), pravá = PO (saturace +8 %)
- **Jeden objekt musí diagonálu překročit** (sekačka, nůžky) → vytváří hloubku a děj

### C13 — Yellow Campaign Badge
Pro novinky ve službách. Žlutá `#FFD54F` výplň, text `#1E5A32` Montserrat 800.
Tvar: pilulka nebo trojúhelník. `NOVINKA` + název služby.
**Aktivuje pravidlo „žlutá 1× na plátno"** — pokud je badge, nikde jinde žlutá nesmí být.

### C14 — QR Card (tisk)
Bílá karta radius 12, QR uvnitř, pod ním `Napište nám` Poppins 500.
- Minimum 22 × 22 mm (DL/A5), 45 × 45 mm (A3), 90 × 90 mm (roll-up/banner)
- Cíl: `wa.me/420730588372?text=Ahoj%20zajímá%20mě%20seknuto`
- **AI generuje pouze šedý placeholder s rohovými značkami.** Reálný QR se vkládá v post-produkci.

---

<a id="6"></a>
## 6. LAYOUT CHASSIS — 5 ZÓN + REFLOW

> Jeden kostra, všechny formáty. Zóny se nemění — mění se jen jejich výšky a řazení podle poměru stran.

```
┌─────────────────────────────────────────┐
│ ZÓNA 1 — IDENT     C1 lockup · C2 status│  8–12 %
├─────────────────────────────────────────┤
│ ZÓNA 2 — CONTEXT   C3 eyebrow · C4 chipy│  6–11 %
├─────────────────────────────────────────┤
│                                         │
│ ZÓNA 3 — HERO      C5 ladder + fotka    │  38–55 %
│                                         │
├─────────────────────────────────────────┤
│ ZÓNA 4 — PROOF     C6 body · C7 karta   │ 12–20 %
│                    C8 list cards        │
├─────────────────────────────────────────┤
│ ZÓNA 5 — ACTION    C11 micro · C9 CTA   │ 14–22 %
│                    C10 footer           │
└─────────────────────────────────────────┘
```

### 6.1 Reflow tabulka

| Formát | Z1 | Z2 | Z3 | Z4 | Z5 | Specifika |
|---|---|---|---|---|---|---|
| **1:1** (1080×1080) | 11 % | 9 % | 42 % | 17 % | 21 % | Fotka = pravých 42 % šířky, cutout do tmy |
| **4:5** (1080×1350) | 10 % | 8 % | 47 % | 15 % | 20 % | Ladder může být 4 řádky vysoký |
| **9:16 story** (1080×1920) | 9 % | 7 % | 34 % | 30 % | 20 % | Z4 nese C8 list cards; UI safe zóny! |
| **1.91:1 banner** (1920×1005) | 14 % | 11 % | 46 % | — | 29 % | Horizontální split 55/45, Z4 splynuto do Z5 |
| **DL leták** (99×210 mm) | 12 % | 6 % | 46 % | 14 % | 22 % | C12 diagonála místo dark canvasu |
| **A5 leták** (148×210 mm) | 13 % | 8 % | 40 % | 17 % | 22 % | Tisk: bez gridu, bez glow |
| **A3 plakát** (297×420 mm) | 12 % | 7 % | 44 % | 15 % | 22 % | Vše ×1,4 typografická váha |
| **Roll-up** (850×2000 mm) | 15 % | 6 % | 40 % | 17 % | 22 % | Z5 v úrovni očí = 140–170 cm |

### 6.2 Zlaté poměry — tvrdá pravidla

1. **Z3 (HERO) je vždy největší zóna.** Když není, layout je rozbitý.
2. **Z5 (ACTION) nikdy pod 14 %.** CTA musí dýchat.
3. **Součet Z1+Z2 nikdy nad 22 %.** Hlavička není obsah.
4. **Fotka zabírá 38–48 % plochy** u digitálu, 45–55 % u tisku.
5. **Bez obsahu min. 35 % plochy.** Měř to.

### 6.3 Horizontální mřížka
12 sloupců, gutter 2 % kratší hrany, vnější margin 5,5 %.
Obsah se drží ve sloupcích 1–7 (levý blok) a 8–12 (fotka / proof karta).

---

<a id="7"></a>
## 7. FOTOGRAFIE & BRAND HUMAN

### 7.1 Brand human — kanonický popis

Muž 30–40 let, tmavě zelené pracovní laclové kalhoty + olivové polo/tričko,
tmavě zelená kšiltovka s logem, hnědé pracovní boty. Krátký vous. Soustředěný,
nikdy do kamery, nikdy úsměv „do fotobanky". V akci — stříhá, kleká, tlačí sekačku.

**Toto je vizuální konstanta.** Ve všech AI generovaných assetech stejná postava, stejné oblečení, stejná barevná logika. Reference: `tmpm3stmvu8__1_.jpg`.

### 7.2 Světelný podpis

| Parametr | Hodnota |
|---|---|
| Denní doba | Zlatá hodina — ráno nebo večer, nikdy poledne |
| Směr světla | Protisvětlo / zezadu-zprava, rim light na rameni a čepici |
| Hloubka ostrosti | Mělká — pozadí rozostřené (f/2.0–2.8 look) |
| Barevná teplota | Teplá 5200–5600 K, zelená v listech sytá, ne neonová |
| Kontrast | Vysoký, hluboké stíny — musí sednout do dark canvasu |

### 7.3 Blending fotky do dark canvasu (klíčová technika)

Fotka **nikdy nemá ostrý obdélníkový okraj**. Napojení:
1. Levá hrana fotky → `gradient.photo_fade` (fotka mizí do tmy směrem doleva)
2. Spodní hrana → `gradient.bottom_scrim`
3. Barevná harmonizace: stíny fotky posunout do zelené (`#0F2C1C` multiply 15 %)
4. Světelný kužel (vrstva 3) prochází přes fotku → sjednocuje ji s pozadím

### 7.4 Před/po — pravidla

- Stejný úhel, stejná výška objektivu, stejné ohnisko. Jinak pár nefunguje.
- PŘED: desaturace −20 až −25 %, chladnější, mírně tmavší
- PO: saturace +8 %, kontrast +3 %, teplota +200 K
- **Test 1 sekundy:** cizí člověk musí okamžitě pochopit změnu. Pokud po vypadá jako „jiný záběr téhož", pár je slabý → nepoužívat.
- **Reálné fotky zákazníka se NIKDY nepřekreslují.** Pouze color grading v uvedených limitech.

### 7.5 Zakázané ve fotografii

❌ Stock fotky s vodoznakem · ❌ Úsměv do kamery · ❌ Prázdná dokonalá zahrada bez člověka jako hero · ❌ Modré nebe jako dominantní plocha (to je jiný brand) · ❌ Rotace vstupní fotky o 90° · ❌ Více než 2 osoby v záběru

---

<a id="8"></a>
## 8. FORMÁTOVÁ MATICE

| Asset | Rozměr | Poměr | Systém | Grid | Glow | QR | Cena |
|---|---|---|---|---|---|---|---|
| IG post | 1080×1080 | 1:1 | Dark Emerald | ✅ | ✅ | ❌ | ❌ |
| IG post portrait | 1080×1350 | 4:5 | Dark Emerald | ✅ | ✅ | ❌ | ❌ |
| IG / FB story | 1080×1920 | 9:16 | Dark Emerald | ✅ | ✅ | ❌ | ❌ |
| Reels cover | 1080×1920 | 9:16 | Dark Emerald | ✅ | ✅ | ❌ | ❌ |
| Highlight cover | 1080×1920 | 9:16 | Dark, jen ikona | ❌ | jemný | ❌ | ❌ |
| OG / web banner | 1920×1005 | 1.91:1 | Dark Emerald | ✅ | ✅ | ❌ | ❌ |
| Firmy.cz cover | 800×600 | 4:3 | Dark Emerald | ✅ | ✅ | ❌ | ❌ |
| Sklik display | dle formátu | — | **Foto bez textu** | ❌ | ❌ | ❌ | ❌ |
| DL leták | 99×210 mm | — | Diagonal Split | ❌ | ❌ | ✅ 22 mm | ❌ |
| A5 leták | 148×210 mm | — | Diagonal Split | ❌ | ❌ | ✅ 30 mm | ❌ |
| A3 plakát | 297×420 mm | — | Diagonal Split | ❌ | ❌ | ✅ 45 mm | ❌ |
| Roll-up | 850×2000 mm | — | Dark Emerald tisk | ❌ | ❌ | ✅ 90 mm | ❌ |
| PVC banner | dle zakázky | — | Dark Emerald tisk | ❌ | ❌ | volitelně | ❌ |
| Vizitka | 90×50 mm | — | Dark Emerald | ❌ | ❌ | ✅ 18 mm | ❌ |
| Windshield card | 1050×600 px | 1.75:1 | Dark Emerald | ❌ | ❌ | ✅ | ❌ |

**Tiskové konstanty:** 300 DPI · CMYK · bleed 3 mm · safe zone 5 mm · papír 170–250 g/m² silk.
**Digitální konstanty:** RGB · 72–144 DPI · export JPG q90 (foto) nebo PNG (grafika bez fotky).

> **Cena: nikdy na zákaznickém materiálu.** Vždy `Cena na míru · Kalkulace zdarma`.

---

<a id="9"></a>
## 9. COPY SYSTÉM & TEXTOVÉ BANKY

### 9.1 Hierarchie sdělení (vždy v tomto pořadí)

```
KDO      → SeknuTo.cz (lockup)
KDE      → Dvůr Králové a okolí (eyebrow)
CO       → chipy služeb
PROČ     → headline ladder (emoce, ne funkce)
DŮKAZ    → 20+ spokojených zákazníků / hodnocení
JAK      → CTA + telefon
```

Divák musí pochopit KDO + CO + JAK SE OZVAT do **2 sekund**.

### 9.2 Headline bank (LOCKED — nevymýšlet nové bez schválení)

| Ladder | Použití |
|---|---|
| `ZAHRADA` / `NA KTERÉ` / `ZÁLEŽÍ.` | univerzální hero, nejsilnější |
| `POZEMEK` / `KTERÝ` / `DÝCHÁ.` | čištění, přerostlé plochy |
| `PRÁCE` / `KTEROU` / `NEUVIDÍTE.` | pravidelná údržba (přijedeme bez vás) |
| `ZAROSTLÉ` / `DNES` / `HOTOVO.` | rychlá zakázka, urgence |
| `BEZPLATNÁ` (outline) / `KALKULACE` | akviziční, nabídkový |
| `HLEDÁME POSILY` / `DO TÝMU` | nábor |
| `Sekáme.` / `Kácíme.` / `Čistíme.` | tisk — DL, A5, A3 (sentence case!) |

### 9.3 Eyebrow bank
`PROFESIONÁLNÍ PÉČE O ZAHRADU · Dvůr Králové a okolí`
`SPRÁVCE POZEMKŮ A NEMOVITOSTÍ · Dvůr Králové a okolí`
`Zahrada od A do Z`
`Pozemky · Nemovitosti · Zahrady`

### 9.4 Chip bank (vyber 3–4)
`Sekání trávy` · `Kácení stromů` · `Střih keřů a tújí` · `Čištění pozemků` ·
`Hrubé čištění pozemků` · `Realizace zahrad` · `Pravidelná údržba` · `VIP servis` ·
`Odvoz bioodpadu` · `Tlakové mytí` · `Do 48 h`

### 9.5 CTA bank
| Text | Kontext |
|---|---|
| `Zavolat & domluvit prohlídku` | hlavní akviziční |
| `Chci nezávaznou poptávku` | kalkulace, formulář |
| `ZAVOLEJTE 730 588 372` | banner, tisk |
| `Napiš do DMs →` | nábor, sociální |
| `Rezervace zde` / `nebo DM →` | story dvousloupcové |

### 9.6 Proof bank
`20+ spokojených zákazníků` · `Hodnocení na Google ★★★★★` ·
`Cena na míru · Kalkulace zdarma` · `Bez závazku · cena do 24 hodin` ·
`Bezplatná prohlídka · Cena předem · žádné skryté poplatky` ·
`Foto report po každé zakázce`

### 9.7 Micro CTA bank
`Pošli foto zahrady — nabídka ZDARMA 📸` · `Napište nám` · `Ozvi se →` ·
`Jsi to ty? Ozvi se mi v DMs`

### 9.8 Copy pravidla

- Věty na materiálech **max 8 slov**
- Vždy „my/tým", nikdy „já"
- Zákazník na tisku a webu: **Vy/Vám/Váš** (velké V). Nábor a mladší publikum: ty
- Nikdy: „levně", „nejlevnější", „akce", „sleva %" na vizuálech
- Tečka na konci headlinu = povinná. Vykřičník = jen u náboru

---

<a id="10"></a>
## 10. ČESKÁ DIAKRITIKA — ENFORCEMENT

> **Jedna chyba v háčku zničí dojem profesionality celého materiálu.** Nulová tolerance.

### 10.1 Vysoce rizikové (vždy character-by-character do promptu)

| Slovo | Rozklad | Časté chyby |
|---|---|---|
| `Dvůr` | D-v-**ů**-r — ů má KROUŽEK (ne čárku, ne přehlásku) | Dvur, Dvúr, Dvür |
| `Králové` | K-r-**á**-l-o-v-**é** | Kralove |
| `ZÁLEŽÍ` | Z-**Á**-L-E-**Ž**-**Í** | ZALEZI, ZÁLEZÍ |
| `KTERÉ` | K-T-E-R-**É** | KTERE |
| `tújí` | t-**ú**-j-**í** — ú má ČÁRKU (ne kroužek) | tuji, tůjí |
| `Čištění` | **Č**-i-**š**-t-**ě**-n-**í** | Cisteni |
| `Stříhání` | S-t-**ř**-**í**-h-**á**-n-**í** | Strihani |
| `Potřebujete` | ř sedí NA písmenu r po t | Pťřebujete |
| `pozemků` | ů KROUŽEK | pozemku |
| `stromů` | ů KROUŽEK | stromu |
| `zákazníků` | **á** + **í** + **ů** KROUŽEK | zakazniku |
| `údržba` | **ú** ČÁRKA + **ž** | udrzba |
| `péče` | p-**é**-**č**-e | pece |
| `Volejte` | jedno slovo, BEZ mezer mezi písmeny | V o l e j t e |
| `přerostlá` | **ř** + **á** | prerostla |
| `Napište` | **š** | Napiste |
| `bezplatná` | **á** | bezplatna |
| `nezávaznou` | **á** | nezavaznou |
| `spokojených` | **ý** | spokojenych |

### 10.2 Měsíce
`leden · únor(ú) · březen(ř) · duben · květen(ě) · červen(č) · červenec(č,č) · srpen · září(á,ř,í) · říjen(ř,í) · listopad · prosinec`

### 10.3 Lokality
`Dvůr Králové`(ů+á+é) · `Trutnov` · `Vrchlabí`(í) · `Hostinné`(é) · `Jaroměř`(ě+ř) ·
`Náchod`(á) · `Červený Kostelec`(Č+ý) · `Hradec Králové`(á+é) · `Žireč`(Ž+č) · `Bílá Třemešná`(í+ř+ě)

### 10.4 Trojitá ochrana (povinná v každém promptu)
1. V sekci layoutu, kde slovo vzniká
2. V bloku `DIACRITICS VERIFICATION TABLE`
3. V `NEGATIVE PROMPT` jako konkrétní chybný tvar

---

<a id="11"></a>
## 11. MASTER PROMPT GENERÁTOR

> Toto je šablona, kterou Claude vyplňuje. Pořadí sekcí je závazné — modely parsují lépe strukturovaný vstup než souvislý blok.

### 11.1 Model default

```javascript
{
  model: "google/nano-banana-2",
  image_input: [
    "logo.png",        // IMAGE 1 — vždy logo, nikdy překreslovat
    "brand_human.jpg", // IMAGE 2 — konzistentní postava (volitelné)
    "before.jpg",      // IMAGE 3 — pouze u před/po
    "after.jpg"        // IMAGE 4 — pouze u před/po
  ],
  aspect_ratio: "1:1",   // dle formátové matice
  resolution: "4K",
  google_search: false,  // pro brand assety vypnout — plete grounding
  image_search: false,
  output_format: "jpg"
}
```

### 11.2 Skeleton promptu (kopíruj strukturu doslova)

```
[BLOK 0 — PRODUCTION GUARD]
You are producing FINAL PRODUCTION artwork, ready to publish without any editing.
Every specification below is an INSTRUCTION for you to follow, NOT text to display.
Render ZERO technical annotations, dimension markers, px/mm labels, wireframe boxes,
zone names, layer names, font names, or construction lines.

[BLOK 1 — CANVAS & SYSTEM]
Format: [1:1 square 1080×1080 / 9:16 / 1.91:1] · SeknuTo.cz "Dark Emerald" brand system.
Background build, bottom to top:
 1. Radial emerald gradient, light centre upper-right: deep green #17422A into #0F2C1C
    into #0A1F14 into near-black #060D09 at the edges.
 2. Very faint technical grid of thin white lines at 3.5% opacity, evenly spaced.
 3. ONE soft volumetric light shaft entering from the upper-right corner, angled down-left,
    pale green-white, low opacity.
 4. Radial vignette darkening all four edges.
 5. Four thin green corner brackets #3FA34D at 65% opacity, one in each corner, inset
    from the edges, L-shaped outlines only — exactly four, never two, never filled.

[BLOK 2 — REFERENCE IMAGES]
IMAGE 1 = SeknuTo.cz logo. Place it as-is. NEVER redraw, restyle, or reinterpret the logo.
IMAGE 2 = the brand worker photo. Preserve his face, clothing and pose exactly.
Apply only +5% saturation and +3% contrast. Do not regenerate the person.

[BLOK 3 — RENDER ONLY THESE EXACT STRINGS]
'SeknuTo.cz' | '[status]' | '[eyebrow]' | '[chip1]' | '[chip2]' | '[chip3]' |
'[ladder1]' | '[ladder2]' | '[ladder3]' | '[proof]' | '[body1]' | '[body2]' |
'[micro]' | '[cta]' | '730 588 372'
No other text may appear anywhere on the canvas.

[BLOK 4 — ELEMENT COUNT LOCK]
Exactly 1 logo lockup · exactly 1 status pill · exactly 1 headline block ·
exactly 1 glass proof card · exactly 1 green CTA button · exactly 4 corner brackets ·
exactly 1 light shaft · exactly [N] service chips.
Any element appearing twice is a failure.

[BLOK 5 — CANVAS BUILD, TOP TO BOTTOM]
[SECTION 1 — BRAND LOCKUP, upper-left] ...
[SECTION 2 — STATUS PILL, upper-right] ...
[SECTION 3 — EYEBROW LINE] ...
[SECTION 4 — SERVICE CHIPS] ...
[SECTION 5 — HEADLINE LADDER] three stacked uppercase lines in condensed geometric
  extra-bold sans: first line in faint translucent white, second line in pure white,
  third line in brand green #3FA34D ending with a full stop. Lines almost touching.
[SECTION 6 — HERO PHOTO, right side] ...
[SECTION 7 — GLASS PROOF CARD] ...
[SECTION 8 — ACCENT RULE + BODY] ...
[SECTION 9 — MICRO CTA LINE] ...
[SECTION 10 — PRIMARY CTA BUTTON] full-width rounded button, gradient from #4FBF5E to
  #2E8B41, soft green outer glow, thin light highlight along the top inner edge,
  white bold centred label. This is the only glowing element on the canvas.
[SECTION 11 — CONTACT FOOTER] ...

[BLOK 6 — DIACRITICS VERIFICATION TABLE]
ZÁLEŽÍ = Z-Á-L-E-Ž-Í (Á acute, Ž caron, Í acute) — never ZALEZI
Dvůr = D-v-ů-r (ů has a RING above, not an acute) — never Dvur
[... každé české slovo, které se renderuje ...]

[BLOK 7 — MUST NEVER DO]
Never redraw the logo · never duplicate any element · never render font names ·
never render dimension numbers · never show prices · never add a second glowing element ·
never use yellow more than once · never place letters of a Czech word apart ·
never write [konkrétní chybné tvary] · never add extra text ·
never rotate the input photos · never apply heavy filters or lens flare.
```

### 11.3 JSON obal (pro forge / registry)

```json
{
  "meta": {
    "brand": "SeknuTo.cz",
    "system": "Dark Emerald v3.0",
    "format": "instagram_post_1x1",
    "prompt_version": "v3.0.0",
    "model": "google/nano-banana-2"
  },
  "variables": {
    "STATUS": "Přijímáme objednávky",
    "EYEBROW": "PROFESIONÁLNÍ PÉČE O ZAHRADU · Dvůr Králové a okolí",
    "CHIPS": ["Sekání trávy", "Kácení stromů", "Střih keřů a tújí"],
    "CHIP_FILLED_INDEX": 1,
    "LADDER": ["ZAHRADA", "NA KTERÉ", "ZÁLEŽÍ."],
    "PROOF": "20+ spokojených zákazníků",
    "BODY": ["Sekání, kácení stromů, živé ploty, výsadba.", "Cena vždy po domluvě a bezplatné prohlídce."],
    "MICRO": "Pošli foto zahrady — nabídka ZDARMA 📸",
    "CTA": "Zavolat & domluvit prohlídku",
    "PHONE": "730 588 372"
  },
  "variant_axes": {
    "ladder_treatment": "ghost_white_green",
    "cta_style": "full_width_glow",
    "proof_component": "glass_stars",
    "photo_treatment": "right_cutout_fade",
    "accent_usage": "none"
  },
  "final_prompt": "…",
  "negative_prompt": "…",
  "rubric_target": 88
}
```

---

<a id="12"></a>
## 12. NEGATIVE PROMPT — LOCKED MASTER STRING

> Vlož do **každého** promptu. Formátově specifické dodatky se připojují za tento blok.

```
dimension labels visible, px measurements, mm labels, zone names visible,
section headers visible, layer names, font names visible, Poppins text, Montserrat text,
wireframe boxes, annotation text, ruler marks, construction lines, guide lines,
draft marks, measurement arrows, lorem ipsum, placeholder brackets, curly braces,
duplicate logo, two logos, duplicate CTA button, two buttons, duplicate proof card,
two status pills, more than four corner brackets, two light shafts,
second glowing element, multiple yellow elements,
redrawn logo, distorted logo, wrong logo colours, extra grass blades,
missing Czech diacritics, ZALEZI, KTERE, Dvur, Kralove, tuji, Cisteni, Strihani,
Pťřebujete, Napiste, pozemku without ring, stromu without ring, zakazniku,
letters spaced apart in Czech words, V o l e j t e,
visible prices, Kč amounts, per square metre pricing, discount badges,
stock watermark, getty watermark, shutterstock,
lens flare, heavy HDR, cartoon style, 3D render look, illustration style,
oversaturated neon green, blue sky dominant background, white background,
smiling at camera, more than two people, rotated photo, mirrored text,
blurry text, pixelated text, compression artifacts, low resolution,
Comic Sans, Times New Roman, Arial, serif fonts
```

---

<a id="13"></a>
## 13. QA RUBRIKA 0–100

> Toto je **hodnotící funkce** pro auto-critique (vision model) i pro lidskou kontrolu.
> Výstup pod **80 bodů se nepublikuje**. Výstup s jakýmkoli HARD FAIL se zahazuje bez ohledu na skóre.

### 13.1 Kritéria a váhy

| # | Kritérium | Váha | Co se hodnotí |
|---|---|---|---|
| 1 | **Diakritika** | 15 | Každé české slovo správně. Jediná chyba = HARD FAIL |
| 2 | **Brand rozpoznatelnost** | 12 | Dark emerald + brackets + lockup + ladder přítomny |
| 3 | **Čistota textu** | 10 | Žádné artefakty, deformace, zdvojená písmena |
| 4 | **Headline ladder** | 10 | Tři úrovně, správné barvy, tečka na konci |
| 5 | **Barevná věrnost** | 10 | Odstíny sedí na tokeny, žádná cizí barva |
| 6 | **Zónové proporce** | 10 | Z3 největší, Z5 ≥ 14 %, Z1+Z2 ≤ 22 % |
| 7 | **CTA dominance** | 10 | Právě jeden zářící CTA, telefon čitelný na 2 m |
| 8 | **Počet prvků** | 8 | Žádné duplikáty, chipy ≤ 4, textové bloky ≤ 6 |
| 9 | **Integrita fotky** | 8 | Postava nepřekreslená, správná orientace, blending |
| 10 | **Dýchání layoutu** | 7 | ≥ 35 % prázdné plochy, nic se nedotýká hran |
|  | **Celkem** | **100** | |

### 13.2 HARD FAIL — okamžité zahození

- Jakákoli chyba v diakritice
- Viditelná technická anotace (px, mm, „ZONE", název fontu)
- Jakákoli konkrétní cena
- Zdvojený unikátní prvek (logo, CTA, proof karta)
- Překreslené / deformované logo
- Žlutá použitá více než jednou
- Druhý zářící prvek vedle CTA
- Text přeložený do angličtiny

### 13.3 Prahy

| Skóre | Akce |
|---|---|
| 92–100 | Publikovat + uložit jako nový baseline pro daný formát |
| 80–91 | Publikovat |
| 65–79 | Jedna cílená iterace (opravit **jednu** věc) |
| < 65 | Zahodit, přegenerovat s jiným variant vektorem |

---

<a id="14"></a>
## 14. NAPOJENÍ NA SEKNUTO-FORGE

> Cíl: systém, který se **sám zlepšuje**, ne knihovna, kterou musíš ručně obsluhovat.

### 14.1 Datový tok

```
design-system.md (tento soubor)
        │  tokeny + chassis + banky
        ▼
  PROMPT BUILDER  ──►  variant vektor (epsilon-greedy)
        │
        ▼
  REPLICATE (nano-banana-2)  ──►  obrázek
        │
        ▼
  VISION AUTO-CRITIQUE  ──►  rubrika §13  ──►  skóre 0–100 + seznam vad
        │
        ├── skóre ≥ 92  →  ulož jako BASELINE daného formátu, zvyš váhu variantu
        ├── 80–91       →  publikuj, loguj
        ├── 65–79       →  jedna cílená iterace (jen jedna vada!)
        └── < 65        →  zahoď, sniž váhu variantu
        │
        ▼
  MONGODB / JSON  ──►  prompt_id · variant · skóre · vady · asset URL
```

### 14.2 Variant osy pro bandit loop

Bandit optimalizuje **jen tyto osy**. Vše ostatní je zamčené (§15) — jinak systém driftuje.

| Osa | Hodnoty |
|---|---|
| `ladder_treatment` | `ghost_white_green` · `outline_solid` · `white_green_only` |
| `cta_style` | `full_width_glow` · `pill_compact` · `split_two_column` |
| `proof_component` | `glass_stars` · `inline_text` · `list_cards` · `none` |
| `photo_treatment` | `right_cutout_fade` · `full_bleed_scrim` · `no_photo_typographic` |
| `accent_usage` | `none` · `yellow_new_tag` · `yellow_campaign_badge` |
| `chip_count` | `2` · `3` · `4` |
| `light_shaft_intensity` | `subtle` · `pronounced` |

**Odměna** = skóre z rubriky. **HARD FAIL** = odměna 0 a okamžité zahození varianty pro daný běh.

### 14.3 Struktura promptu v registru

```
prompts/
  ├── _system/
  │     ├── tokens.json          ← §2, generováno z tohoto souboru
  │     ├── negative.txt         ← §12, LOCKED
  │     └── rubric.json          ← §13
  ├── instagram_post_1x1/
  │     ├── baseline.json        ← nejlepší dosažené skóre
  │     └── variants/
  ├── story_9x16/
  ├── og_banner_191x1/
  ├── dl_flyer/
  └── a3_poster/
```

### 14.4 Pravidlo povyšování baseline

Nový baseline se nastaví **jen** když varianta dosáhne skóre ≥ 92 **a zároveň** nemá žádný HARD FAIL **ve dvou po sobě jdoucích generacích**. Jednorázový šťastný výstup baseline nepřepisuje.

---

<a id="15"></a>
## 15. EVOLUCE — CO JE LOCKED, CO SE SMÍ MĚNIT

### 🔒 LOCKED — mění se pouze major verzí (v4.0) a jen po vědomém rozhodnutí

- Logo a jeho barvy · web `SeknuTo.cz` (velké T) · telefon `730 588 372`
- Barevná paleta (6 zelených + žlutá + červená)
- Montserrat + Poppins
- Pětivrstvý canvas systém
- Corner brackets
- Headline ladder jako signature device
- Diagonála 42–45° pro tisk
- Pětizónový chassis
- Pravidlo „jedna zářící akce"
- Pravidlo „žádné ceny na zákaznickém materiálu"

### 🔄 VARIABLE — mění se per asset, bez povýšení verze

- Texty z bank (§9) · výběr chipů · fotografie · lokalita a datum
- Variant osy z §14.2
- Poměry zón v rámci rozsahů z §6.1

### 📈 Protokol povýšení verze

```
v3.0 → v3.1   Přidána komponenta nebo hodnota do banky (zpětně kompatibilní)
v3.x → v3.x+1 Změna proporcí, nová varianta stávající komponenty
v3.x → v4.0   Změna LOCKED prvku — vyžaduje: 1) důvod, 2) A/B důkaz,
              3) přegenerování baseline pro všechny formáty
```

**Železné pravidlo iterace:** jedna verze opravuje **jeden** problém. Když opravíš pět věcí najednou a výsledek je horší, nevíš co to způsobilo. Toto pravidlo stálo devět měsíců, než se naučilo.

---

<a id="16"></a>
## 16. FAILURE LOG v3

> Přenesené z v1–v2 + nové z výroby dark emerald série. Každá položka = reálná chyba.

| # | Chyba | Příčina | Fix |
|---|---|---|---|
| F1 | `{{PLACEHOLDER}}` vykreslen do obrázku | šablona se dostala k modelu | Nahradit všechny sloty finálním textem před odesláním |
| F2 | Slovo „Poppins" v obrázku | název fontu v promptu | Psát „geometric sans-serif extra-bold" |
| F3 | „90×5" vykresleno jako text | rozměry v promptu | Jen sémantický popis, nikdy čísla |
| F4 | Před/po prohozené | vágní popis stavů | Explicitní vizuální popis OBOU stavů |
| F5 | Duplicitní PO badge | chybí count lock | Trojitá ochrana: sekce + count lock + negative |
| F6 | `V o l e j t e` | „wide letter-spacing" v promptu | „single word, letters touching normally" |
| F7 | `Pťřebujete` | chybí character breakdown | Rozklad po písmenech do promptu |
| F8 | AI překreslila fotku zákazníka | ideogram neumí reference | nano-banana-2 + „never regenerate" |
| F9 | Spodní zóna 40 % plátna | CTA dostalo moc místa | Z5 max 22 % |
| F10 | Polaroid schoval hero | špatná velikost a pozice | max 25 % šířky, upper-left |
| F11 | Generic „Hotovo." místo služby | plýtvání hero pozicí | Konkrétní služba = headline |
| F12 | AFTER zoomnutý na detail | nespecifikovaný framing | „wide establishing shot, full scope" |
| F13 | Fotka otočená o 90° | model ji cpal do fixního rámu | „never rotate, frame adapts to photo" |
| F14 | Přepálené barvy fotek | model „vylepšuje" | Explicitní limity +5 % / −10 % |
| **F15** | **Dvě žluté v jednom plátně → obě zanikly** | chybí pravidlo unikátnosti akcentu | Žlutá právě 1×, jinak vůbec |
| **F16** | **Dva zářící prvky (CTA + badge) → rozpad hierarchie** | glow použit jako dekorace | Glow výhradně na primárním CTA |
| **F17** | **Headline ladder o 4 řádcích → nečitelný** | příliš dlouhý text | Max 3 řádky, každý max 2 slova |
| **F18** | **Fotka s ostrým obdélníkovým okrajem v dark canvasu** | chybí photo_fade | Vždy gradient maska do tmy |
| **F19** | **Corner brackets jen ve dvou rozích** | model je „ušetřil" | „exactly four, one in each corner" v count locku |
| **F20** | **Grid příliš viditelný → vypadá jako tabulka** | krytí nad 6 % | Držet na 3,5 %, u tisku vynechat |
| **F21** | **Chipy v jedné řadě přetekly okraj** | 5+ chipů | Max 4 chipy, jinak dvě řady |
| **F22** | **Wordmark „SeknuTo.cz" s malým T** | model normalizoval psaní | Explicitně: „capital T mid-word, brand stylization" |

---

<a id="17"></a>
## 17. PRE-FLIGHT CHECKLIST

Projít **před odesláním do generátoru**:

**Systém**
- [ ] Formát vybrán z matice §8, chassis proporce z §6.1
- [ ] Všech pět vrstev canvasu popsáno v pořadí
- [ ] Corner brackets: „exactly four"
- [ ] Světelný kužel: „exactly one"

**Text**
- [ ] Všechny texty z bank §9 — nic vymyšleného
- [ ] Headline ladder max 3 řádky, tečka na konci
- [ ] `SeknuTo.cz` s velkým T
- [ ] Žádná cena, žádné Kč
- [ ] Diakritická tabulka §10 obsahuje každé renderované slovo
- [ ] Textových bloků ≤ 6

**Komponenty**
- [ ] Element count lock vypsán pro každý unikátní prvek
- [ ] Právě jedno CTA se září
- [ ] Žlutá 0× nebo 1×
- [ ] Chipů 2–4, právě jeden filled

**Fotka**
- [ ] Logo jako image reference, nikdy překreslované
- [ ] „never regenerate / never rotate" v promptu
- [ ] Color grading limity uvedeny
- [ ] Blending do tmy popsán

**Guard**
- [ ] Production guard blok na začátku
- [ ] MUST NEVER DO blok na konci
- [ ] Master negative prompt §12 přiložen
- [ ] Konkrétní chybné tvary slov v negative

**Po generaci**
- [ ] Oskórováno rubrikou §13
- [ ] Žádný HARD FAIL
- [ ] Skóre ≥ 80 → publikovat · ≥ 92 → nastavit jako baseline

---

## 📌 ZÁVĚREČNÝCH 10 PRAVIDEL (kdyby zbyla jen jedna stránka)

1. **Dark emerald canvas, pět vrstev, vždy.** To je rozpoznatelnost.
2. **Headline ladder: ghost → bílá → zelená, s tečkou.** To je podpis.
3. **Jedno zářící CTA na plátně.** Nic jiného nemá glow.
4. **Žlutá maximálně jednou.** Jinak to není akcent.
5. **Nikdy ceny.** „Cena na míru · Kalkulace zdarma."
6. **Logo se nikdy nepřekresluje.** Vždy image reference.
7. **Diakritika je priorita číslo jedna.** Jeden háček zničí celý materiál.
8. **35 % plátna zůstává prázdných.** Ticho je součást luxusu.
9. **Jedna iterace opravuje jednu věc.** Vždy.
10. **Funguje to? Zamkni to a měň jen proměnné.** Konzistence staví brand, variace ho rozbíjí.

---

**SeknuTo.cz — Sekáme. Kácíme. Čistíme.**
*Staráme se o váš pozemek od A do Z.*

`Dark Emerald v3.0` · srpen 2026 · nahrazuje `design-system.md v1`
Umístění: `/mnt/skills/user/seknuto/references/design-system.md` + projektové soubory
