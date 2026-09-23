# Portfolio Allocation Optimizer

> **Status: authoritative product spec.** Implemented in Streamlit in `app.py` and `optimizer/` (see [Streamlit port](#streamlit-port)). The behaviour below was originally specified for a React prototype built in Figma Make whose source is **not in this repo**; its stack, build and file layout live in [FIGMA_MAKE.md](FIGMA_MAKE.md). Where the port differs from this spec, the deviation is listed below. Unresolved contradictions are listed under [Open questions](#open-questions).

A single-page app for managing and analysing marketing spend across a hierarchy: **Portfolio → Brands → Categories → Segments**. Each level's percentages must independently sum to 100%. Actual campaign results can be entered and compared against budget.

---

## Streamlit port

| Concern | Where |
|---|---|
| Entry point, sidebar, view switcher | `app.py` |
| Data model, budget cascade, validation, redistribution, ranking | `optimizer/model.py` |
| CSV import | `optimizer/csv_import.py` |
| Sunburst + radar (Plotly) | `optimizer/charts.py` |
| Tabs and editable tables | `optimizer/views.py` |
| Theme (design tokens) | `.streamlit/config.toml` |
| Tests | `tests/` (`make pytest`) |

State is held in `st.session_state` (in-memory, per browser session). There is no backend.

### Deviations from the spec

| Spec | Streamlit port |
|---|---|
| Drag-handle **slider bar** on Overview | Not ported (Streamlit has no multi-handle slider). Use the suggestion strip or edit values directly |
| Overview edits "all levels" | Overview edits brands and shows a read-only full budget tree. Categories and segments are edited in the **brand tabs** |
| Editable **Total** row rescales `portfolioValue` | The portfolio budget is a number input in the sidebar |
| Click a sunburst arc to filter the Report table | Brand and category **filter dropdowns** above the Report table |
| Radar with category petals and vertex tooltips | Brand polygon and equal-split outline only |
| "Suggestion engine" in Report (undefined in the prototype docs) | Simple rule on % of target: ≥120% → increase, ≤80% → reduce, otherwise hold |
| Tabs | A segmented control; only the active view renders (faster than rendering every tab) |
| DM Sans / DM Mono fonts | Streamlit default sans-serif |
| Adding a brand | New brand starts at 0% with one category and one segment at 100% |

---

## Data model

All state lives in one place. Shown as TypeScript for brevity; the port uses the equivalent dataclasses in `optimizer/model.py`.

```ts
interface Seg   { id: string; name: string; value: number }
interface Cat   { id: string; name: string; value: number; segments: Seg[] }
interface Brand { id: string; name: string; value: number; categories: Cat[] }
```

| State | Type | Default | Description |
|---|---|---|---|
| `brands` | `Brand[]` | 5 brands × 5 cats × 3 segs | Full portfolio tree |
| `portfolioValue` | `number` | `10 000` | Total budget in Can$K |
| `results` | `Record<segId, number>` | `{}` | Actual campaign results in Can$K, keyed by segment ID |

**Budget formula** — value at any node cascades down multiplicatively:

```
brandBudget = portfolioValue × brand% / 100
catBudget   = brandBudget   × cat%   / 100
segBudget   = catBudget     × seg%   / 100
```

---

## Tabs

| Tab | Purpose | Prototype file | Streamlit function |
|---|---|---|---|
| **Overview** | Edit allocations; editable budget cells; add/remove brands | `App.tsx` → `OverviewPanel` | `views.overview` |
| **Brand A–E** | Per-brand category and segment editing with suggestion strips | `App.tsx` → `BrandPanel` | `views.brand_tab` |
| **Results** | Enter actual results by segment/category/brand; CSV import; Score rank; Var vs Budget | `ResultsPanel.tsx` | `views.results_tab` |
| **Report** | Flat segment table with optimisation suggestions; sunburst + radar charts | `Report.tsx` + `ReportVisual.tsx` | `views.report_tab` |

---

## Features

### Slider Bar
Drag the handles between adjacent brand arcs on the Overview tab to redistribute percentages without typing. Adjacent brand values are preserved as a pool — dragging left/right transfers share between neighbours. *(Not ported to Streamlit.)*

### Suggestion Strip
After editing any percentage field, a strip appears showing how to redistribute the slack to other items at the same level. Individual chips apply the full delta to one item; **Spread evenly** distributes it proportionally across all others.

### Editable Budget Cells
Clicking any budget figure in the Overview table opens an inline `Can$K` input. Committing a value back-computes the percentage from `newK / parentBudget × 100`. Editing the **Total** row rescales `portfolioValue` instead.

### Results Entry
In the Results tab, click any **Result** cell to type actual campaign spend in Can$K:
- **Segment level** — sets that segment directly.
- **Category level** — distributes the entered total evenly across its segments.
- **Brand level** — distributes evenly across all segments in all categories.

### CSV Import
Drag a `.csv` file onto the drop zone at the top of the Results tab, or click to browse.

**Required format** (header row mandatory, values in Can$K):

```csv
Brand,Category,Segment,Result
Brand A,Cat A1,Seg A1-1,1500
Brand A,Cat A1,,4500
Brand B,,,12000
```

- All four columns present → sets that specific segment.
- `Segment` blank → distributes result evenly across all segments in that category.
- `Category` and `Segment` blank → distributes evenly across all segments in that brand.
- Name matching is case-insensitive and exact.

### Score & Var Columns (Results tab)
| Column | Description |
|---|---|
| **Budget** | Derived from portfolio allocation (read-only) |
| **Result** | Editable actual campaign spend |
| **Var** | `Result − Budget` — green if positive, red if negative |
| **Score** | Dense rank by Result descending — `#1` = highest result. Shown at segment, category, and brand level. Toggle **▼** header to sort by Score. |

### Sunburst Chart (Report tab)
Three concentric rings: Brands (inner) → Categories (mid) → Segments (outer). Arc **width** = allocation percentage. Arc **brightness** = `result ÷ budget` (% of target achieved):

| Brightness | Meaning |
|---|---|
| Very dark | 0% of target achieved |
| Medium | ~100% of target (on budget) |
| Bright | 150%+ of target (over-performed) |
| Full brand colour | No result entered |

Click a segment arc to filter the Report table to that Brand × Category scope. Click again to clear.

Hover any arc for a tooltip showing: allocation %, Budget, Result, % of target, Var, and Score rank.

### Radar Chart (Report tab)
N-axis spider chart where each axis represents a brand. Polygon area = brand's portfolio share. Dashed outline = ideal equal-split target. Category petals arc around each vertex. Hover vertices and petals for detailed tooltips.

---

## Design tokens

Override these to retheme (React prototype: `src/index.css`; Streamlit port: `.streamlit/config.toml` maps `--bg`, `--surface`, `--text` and `--accent` to the theme, while `--danger` and the chart colours are set in code).

```css
--bg:        #0d0f12   /* page background              */
--surface:   #151820   /* card / panel background      */
--surface-2: #1d2130   /* table header rows            */
--border:    #2a2f3d   /* dividers and outlines        */
--text:      #e8eaf0   /* primary text                 */
--muted:     #6b7280   /* secondary / label text       */
--accent:    #4ade80   /* green — primary interactive  */
--danger:    #f87171   /* red — over-budget / negative */
--warning:   #fbbf24   /* amber — imbalanced levels    */
```

---

## Known limitations

| Limitation | Workaround |
|---|---|
| No persistence — data resets on reload | Serialise `brands`, `portfolioValue`, and `results` to `localStorage` (prototype) or a file/database (Streamlit) |
| Single portfolio — no save/load or multi-scenario | Each browser tab is independent |
| CSV import is additive per segment — importing twice accumulates results *(see Open questions)* | Clear result cells manually before re-importing |
| No authentication or multi-user support | Deploy behind an auth proxy if access control is needed |

---

## Open questions

Contradictions in the original spec. The Streamlit port picked the behaviour in the last column so it could be built; change the port and the spec together once decided. Reasoning and alternatives for each: [DECISIONS.md](DECISIONS.md) (D-06 to D-10).

| Topic | Contradiction | Streamlit port currently |
|---|---|---|
| CSV import | "Sets that specific segment" vs "importing twice accumulates" | **Replaces**: each row sets its segments, so re-importing the same file changes nothing |
| Number of brands | Tabs are "Brand A–E" but Overview can add/remove brands | **Dynamic**: five brands by default, tabs follow the brand list |
| Validation | "Must sum to 100%" but nothing says what happens when they don't | **Warns, never blocks**: amber warning and suggestion strip; budgets use the raw percentages |
| Suggestion strip | "Spread evenly" vs "distributes proportionally" | **Proportional** to current values (button labelled "Spread proportionally") |
| Score | Ranks by absolute Result, so the biggest budget always wins | Kept as specified (rank by Result); ranking by `Result ÷ Budget` would be a product decision |
