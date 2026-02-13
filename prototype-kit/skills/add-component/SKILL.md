---
name: add-component
description: "Use when the user wants to add a new component or new variants of an existing component to the prototype kit. Triggered by pasting Figma CSS, describing a component, or sharing a screenshot."
---

# Add Component to Design System

## When to Use
Use when the user wants to add a new component or new variants of an existing component to the prototype kit. Typically triggered by the user pasting Figma CSS export, sharing a screenshot, or describing a component they need.

## Before You Start

**Read the project-local design-system skill first:** `.claude/skills/design-system/SKILL.md`

This gives you the current token mappings (hex → Tailwind class) and existing component API.

## Workflow

### Step 1: Understand the input

The user will provide one or more of:
- **Figma CSS export** (pasted text) — the primary input
- **A screenshot** of the component
- **A Figma link** (use Figma MCP to inspect if available)
- **A description** of what the component should do

If the input is a CSS export, analyze it to identify:
- Component name and purpose
- All variants (look for repeated blocks with differences)
- Which existing tokens map to the hardcoded values (cross-reference the design-system skill)
- Any values NOT in the token system (flag these)

### Step 2: Check for existing overlap

Read `src/components/ui/index.ts` and check:
- Does this component already exist? → Add variants, not a new file
- Does it overlap with an existing component? → Extend the existing one
- Is it truly new? → Create a new file

### Step 3: Build the component

Create or update the component file at `src/components/ui/{name}.tsx`:

**Follow these patterns:**

```tsx
// Props interface with variant union types
type ComponentVariant = "variant-a" | "variant-b";
type ComponentSize = "sm" | "md" | "lg";

interface ComponentProps {
  variant?: ComponentVariant;
  size?: ComponentSize;
  className?: string;
  children?: React.ReactNode;
}

// Style maps for variants (not inline ternaries)
const variantStyles: Record<ComponentVariant, string> = {
  "variant-a": "bg-surface text-foreground ...",
  "variant-b": "bg-accent text-foreground-on-color ...",
};

// Named export (not default)
export function Component({ variant = "variant-a", ...props }: ComponentProps) {
  return ( ... );
}
```

**Rules:**
- Named export, not default export
- Use Tailwind classes mapped to design tokens — NEVER hardcode hex colors
- Use `Record<Variant, string>` maps for variant styles
- Add `"use client"` only if the component uses hooks or event handlers
- Keep it minimal — no over-engineering
- Match Figma measurements exactly

### Step 4: Update the barrel export

Add the new export to `src/components/ui/index.ts`.

### Step 5: Update the design system skill

Add the component's API reference to `.claude/skills/design-system/SKILL.md` in the Component Library section:

```markdown
### ComponentName
\`\`\`tsx
<ComponentName variant="a|b" size="sm|md" prop={value} />
\`\`\`
Brief description of what it does and when to use each variant.
```

### Step 6: Update the showcase page

Add the new component (with all variants) to `src/app/prototypes/showcase/page.tsx`:
- Add the import from `@/components/ui`
- Add a demo section showing all variants

### Step 7: Verify

Run `npm run build` to confirm everything compiles.

### Step 8: Report back

Tell the user:
- What component was created/updated
- What variants are available
- What props it accepts
- If any new tokens were needed (and whether they were added)

## If the Figma CSS reveals missing tokens

If the CSS contains colors or values not in the token system:
1. Flag it: "This component uses #HEXVAL which isn't in our token system yet"
2. Ask if it should be added as a new token or mapped to an existing one
3. If adding: update both `src/styles/tokens.css` and `src/app/globals.css`
4. Update `.claude/skills/design-system/SKILL.md` with the new token
