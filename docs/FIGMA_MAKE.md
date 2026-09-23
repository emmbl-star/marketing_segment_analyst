# Figma Make scaffold and optimizer prototype

> **Status: reference only.** Describes the React + Vite + Tailwind prototype built in Figma Make. Its source code is **not in this repo**, so the file paths below (`src/…`, `vite.config.ts`, `.mise.toml`) do not exist here. The deployed app is the Streamlit port; see [PORTFOLIO_OPTIMIZER.md](PORTFOLIO_OPTIMIZER.md) for what it should do and [../AGENTS.md](../AGENTS.md) for the repo. Use this file only when generating or editing the React front-end.

React + Vite + Tailwind CSS project running inside Figma Make. This is the single place where the prototype's stack, build and configuration are documented.

## Stack

| Layer | Technology |
|---|---|
| UI | React 19 + React DOM 19, TypeScript 5.7 |
| Build | Vite 8 with `@vitejs/plugin-react` |
| Styling | Tailwind CSS v4 through the `@tailwindcss/vite` plugin |
| Fonts | DM Sans + DM Mono via Google Fonts |
| Formatting | oxfmt |
| Toolchain | Node.js and pnpm, versions pinned in `.mise.toml` |
| Backend | None — all state is in-memory (browser only) |

## Development server

A Vite development server is already running on `$PORT` (default 8443). You don't need to start it manually.

- **Preview URL:** the user can access the running app through the preview panel
- **Hot reload:** changes to source files are reflected immediately

## Build & deploy

```bash
pnpm install    # install dependencies
pnpm build      # outputs to dist/
pnpm preview    # serve dist/ locally on $PORT (default 8443)
```

`dist/` is a fully static site — deploy it to any CDN (Vercel, Netlify, S3 + CloudFront, GitHub Pages, etc.). No server-side logic required.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `8443` | Dev server and preview bind port |
| `FIGMA_PUBLIC_URL` | *(empty)* | Sets Vite `base` path for sub-directory deploys |
| `FIGMA_DEV_SERVER_HOST` | `0.0.0.0` | Dev server bind address |

## Project structure

This is the canonical project structure. Start with task-relevant files below. Only follow imports or inspect other files when required, when a documented path is missing, or when the repository contradicts this guide.

Scaffold files:

- `src/main.tsx` - React entrypoint; imports `src/index.css` and mounts `src/App.tsx` into the `#root` element
- `src/App.tsx` - Primary application component and the usual starting point for UI work. In the optimizer it also holds the root state, tab router, shared types, `OverviewPanel` and `SliderBar`
- `src/index.css` - Global CSS entrypoint, Tailwind CSS v4 import, Google Fonts `@import`, CSS variables and body defaults
- `index.html` - Vite HTML shell containing the `#root` element and loading `src/main.tsx`
- `package.json` - Project dependencies and the Vite build, development, preview, and formatting scripts
- `vite.config.ts` - Vite configuration with React, Tailwind CSS v4, and Figma Make plugins plus the `@` alias for `src`
- `.mise.toml` - Toolchain versions for Node.js and pnpm

Optimizer files added on top of the scaffold:

- `src/Report.tsx` - Report tab: flat segment table, suggestion engine, portfolio-value editor
- `src/ReportVisual.tsx` - SVG charts: sunburst (3 rings) and radar spider
- `src/ResultsPanel.tsx` - Results tab: editable result cells, CSV import, score ranking

## Styling

This project uses Tailwind CSS v4 through the `@tailwindcss/vite` plugin configured in `vite.config.ts`. `src/index.css` imports Tailwind with `@import 'tailwindcss';`. Use Tailwind utility classes directly in JSX and put global CSS or Tailwind v4 theme customization in `src/index.css`. This scaffold does not need a Tailwind config file or PostCSS config.

`src/main.tsx` imports `src/index.css`, so global font wiring belongs in `src/index.css`. Keep CSS `@import` statements first, then add any `@font-face` rules and `font-family` defaults there.

The colour tokens are listed in [PORTFOLIO_OPTIMIZER.md](PORTFOLIO_OPTIMIZER.md#design-tokens); override them in `src/index.css` to retheme without touching components.

## Code quality

- Use double quotes for strings containing apostrophes (`"We're here to help"`), or escape them in single-quoted strings. An unescaped apostrophe in a single-quoted string breaks the build.
- Ensure JSX tags are closed and braces are balanced.
