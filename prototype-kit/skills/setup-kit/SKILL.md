---
name: setup-kit
description: "Use when setting up a new prototype kit for a client. Guides through creating a Next.js project, extracting Figma design tokens, generating components, and creating the project-local design-system skill."
user_invocable: true
---

# Setup Prototype Kit

## Overview

Guided wizard to bootstrap a client-specific rapid prototyping kit. Creates a Next.js 15 + Tailwind v4 project with design tokens extracted from the client's Figma, structural components, and a project-local design-system skill that teaches Claude the client's design language.

## Prerequisites

- Node.js 18+ installed
- Access to the client's Figma design system file (view or edit)
- A target directory for the new project

## Process

Follow these steps IN ORDER. Ask ONE question at a time. Wait for the user's response before proceeding.

### Step 1: Gather Project Info

Ask the user:
1. **Client name** (e.g., "Acme Corp") — used in comments and metadata
2. **Project slug** (e.g., "acme-prototype-kit") — used for directory name and package.json
3. **Token prefix** (e.g., "ac") — short prefix for CSS custom properties like `--ac-brand-500`
4. **Target directory** — where to create the project (default: current working directory)
5. **Primary font** — what font does the client's design system use? (default: Source Sans 3)
6. **Content locale** — what language for placeholder content? (default: English)

### Step 2: Scaffold the Project

Create the following directory structure:

```
[project-slug]/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   └── prototypes/
│   │       └── showcase/
│   │           └── page.tsx
│   ├── components/
│   │   └── ui/
│   │       ├── mobile-layout.tsx
│   │       ├── top-nav.tsx
│   │       ├── bottom-nav.tsx
│   │       └── index.ts
│   └── styles/
│       └── tokens.css          ← empty, filled in Step 3
├── .claude/
│   ├── skills/
│   │   └── design-system/
│   │       └── SKILL.md        ← generated in Step 4
│   └── settings.local.json
├── package.json
├── tsconfig.json
├── postcss.config.mjs
├── next.config.ts
└── CLAUDE.md
```

Use the reference templates from this plugin's `references/` directory. Replace placeholders:
- `[PROJECT_SLUG]` → project slug from Step 1
- `[CLIENT_NAME]` → client name from Step 1
- `[PREFIX]` → token prefix from Step 1
- `[FONT_IMPORT]` → the Google Fonts import name (e.g., `Source_Sans_3`)
- `[FONT_CONSTRUCTOR]` → the font constructor (e.g., `Source_Sans_3`)
- `[FONT_VAR]` → the CSS variable suffix (e.g., `source-sans`)

Copy structural components from `references/components/` into `src/components/ui/`.

Create a minimal `src/app/page.tsx`:
```tsx
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-surface p-8">
      <h1 className="text-2xl font-bold text-foreground mb-4">[CLIENT_NAME] Prototype Kit</h1>
      <p className="text-foreground-secondary mb-8">Prototypes:</p>
      <ul className="space-y-2">
        <li>
          <Link href="/prototypes/showcase" className="text-accent-fg underline">
            Component Showcase
          </Link>
        </li>
      </ul>
    </main>
  );
}
```

Create a minimal `next.config.ts`:
```ts
import type { NextConfig } from "next";
const nextConfig: NextConfig = {};
export default nextConfig;
```

Create `.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": [
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)"
    ]
  }
}
```

Create `CLAUDE.md`:
```markdown
# [CLIENT_NAME] Prototype Kit

## IMPORTANT: How to build in this project
This project has its own design system with tokens, components, and skills. **DO NOT use external plugins for building UI or prototypes.** Instead:
- Read `.claude/skills/design-system/SKILL.md` for tokens, components, and layout patterns
- Read `.claude/skills/add-component/SKILL.md` when adding new components
- All UI work must use the existing design tokens and component library in this project

## Purpose
Rapid functional prototyping environment that mirrors [CLIENT_NAME]'s design system.

## Tech Stack
- Next.js 15 (App Router) + TypeScript
- Tailwind CSS v4
- Figma MCP for design reference

## Project Structure
- `src/app/prototypes/` — prototype pages (one folder per prototype)
- `src/components/ui/` — design system components
- `src/styles/tokens.css` — design tokens as CSS variables
- `src/app/globals.css` — Tailwind theme mapped to tokens
- `.claude/skills/design-system/SKILL.md` — full design system reference

## Rules
- ALWAYS read the design-system skill BEFORE building any UI
- ALWAYS use design tokens via Tailwind classes — never hardcode colors, spacing, or font sizes
- ALWAYS use components from `src/components/ui/` when they exist
- When a needed component doesn't exist yet, create it in `src/components/ui/` following existing patterns
- Use `gap` for spacing between siblings, not `margin`
- Every prototype page goes in `src/app/prototypes/[name]/page.tsx`
- This is a mobile-first app — default viewport is 375px width
- Add new prototypes to `src/app/page.tsx` index page
- Use [LOCALE] for placeholder content
```

After scaffolding, run:
```bash
cd [project-slug] && npm install
```

Verify: `npm run build` should succeed (with empty tokens — colors won't work yet but structure is valid).

### Step 3: Extract Design Tokens from Figma

This is the guided token extraction. Ask the user to do each of these ONE AT A TIME.

**3a: Brand/primary color palette**

Tell the user:
> Open your client's Figma design system file. Go to the color styles or variables panel.
> Find the **primary/brand color palette** (usually 10 shades from dark to light, like 900→50).
> Copy the hex values and paste them here. Format doesn't matter — I'll parse whatever you give me.
>
> Example of what to look for: the main color used for buttons, links, and accents.

Parse the user's input. Map to `--[PREFIX]-brand-900` through `--[PREFIX]-brand-50`.

**3b: Greyscale palette**

Tell the user:
> Now find the **greyscale palette** (neutral colors used for text, backgrounds, borders).
> Same thing — copy the hex values and paste them here.

Parse and map to `--[PREFIX]-grey-*`.

**3c: Additional color palettes (optional)**

Ask:
> Does the design system have additional color palettes beyond the brand color and greyscale?
> (e.g., a secondary brand color, separate status colors like green/red/blue/yellow)
> If yes, paste them. If no, I'll derive status colors from standard defaults.

If the client has custom status colors, add them to tokens.css. If not, use sensible defaults:
- Positive: `#02794F` / surface: `#E6F5EF`
- Negative: `#E14D62` / surface: `#FCEDEF`
- Info: `#4B64D2` / surface: `#EEF0FB`
- Warning: `#A36703` / surface: `#FFF6E2`

**3d: Typography**

Tell the user:
> What are the **typography styles**? Look for heading, label, and paragraph styles with their sizes, weights, and line-heights.
> Paste whatever you see — a table, CSS, or just a list.

Parse and record the typography system.

**3e: Spacing, radii, shadows**

Tell the user:
> Almost done! Do you see any defined:
> - **Border radius** values (e.g., 8px, 12px, 16px, 20px, 32px, 50px)?
> - **Shadow** definitions?
> - **Spacing** scale?
>
> Paste if yes. If the design system doesn't define these explicitly, I'll use sensible defaults.

**3f: Generate the files**

Take all collected values and:
1. Write `src/styles/tokens.css` with all CSS custom properties
2. Update `src/app/globals.css` with the correct `@theme` mappings
3. Update `src/app/layout.tsx` with the correct font import

Verify: `npm run build` should succeed.

### Step 4: Generate the Design-System Skill

Using the collected token data, generate a project-local skill at `.claude/skills/design-system/SKILL.md`.

Fill in:
- Color token tables with actual hex values and Tailwind class mappings
- Typography table with actual styles
- Border radius and shadow tables
- Component library section (start with MobileLayout, TopNav, BottomNav, IconButton)
- Rules section with client-specific locale

Use the design-system template from this plugin as the structural reference, but fill in all values with the client's actual data.

### Step 5: Create Showcase Page

Generate `src/app/prototypes/showcase/page.tsx` that displays:
- All color tokens as colored swatches with labels
- Typography samples for each style
- The three structural components in a demo layout
- Border radius and shadow samples

### Step 6: Create Add-Component Skill

Copy the generic add-component skill into the project at `.claude/skills/add-component/SKILL.md`.

### Step 7: Final Verification & Summary

Run `npm run build` to confirm everything works.

Tell the user:
> Your prototype kit is ready! Here's what was created:
> - **Project:** [project-slug]/
> - **Tokens:** [N] color tokens, [N] typography styles
> - **Components:** MobileLayout, TopNav, BottomNav, IconButton
> - **Skills:** design-system (project-local), add-component (project-local)
>
> To start prototyping:
> ```bash
> cd [project-slug] && npm run dev
> ```
> Then describe any screen and I'll build it using your design system.

### Step 8: Initialize Git & Commit

```bash
cd [project-slug]
git init
git add .
git commit -m "feat: initialize prototype kit with [CLIENT_NAME] design system"
```

## Important Notes

- Ask ONE question at a time throughout this process
- Accept messy input — hex values, CSS blocks, Figma dev mode output, screenshots, tables, lists. Parse whatever the user gives you.
- If a value is unclear, ask for clarification rather than guessing
- Use the reference templates as starting points, not rigid structures — adapt to what the client's design system actually contains
- The goal is a working kit in ~15-20 minutes, not perfection. Components and tokens can be refined later.
