---
name: add-prototype
description: "Use when the user wants to create a new prototype page. Triggered by describing a screen, sharing a screenshot, or asking to build a specific page."
---

# Add Prototype Page

## When to Use
Use when the user wants to create a new prototype page from a description, screenshot, or Figma reference.

## Before You Start

**Read the project-local design-system skill first:** `.claude/skills/design-system/SKILL.md`

This gives you all available tokens, components, typography, and layout patterns.

## Workflow

### Step 1: Understand what to build

The user will provide one or more of:
- **A screenshot** of the target screen
- **A Figma link** (use Figma MCP to inspect if available)
- **A text description** of the page
- **A rough wireframe** description

Identify:
- Page name and purpose
- Key sections/areas of the page
- Which existing components can be reused
- What new components might be needed

### Step 2: Check existing components

Read `src/components/ui/index.ts` and the component library section of the design-system skill.

For each element in the design:
- **Exists?** → Use it
- **Close match?** → Consider extending with a new variant
- **New?** → Flag it, build it using the add-component workflow

### Step 3: Build the page

Create `src/app/prototypes/[page-name]/page.tsx`:

```tsx
"use client";
import { MobileLayout, TopNav, BottomNav } from "@/components/ui";

export default function PageName() {
  return (
    <MobileLayout bg="bg-surface">
      <TopNav title="Page Title" />
      <div className="flex flex-col gap-4 p-4">
        {/* page content using design system components */}
      </div>
      <div className="mt-auto">
        <BottomNav items={[...]} />
      </div>
    </MobileLayout>
  );
}
```

**Rules:**
- Always wrap in `<MobileLayout>`
- Use semantic token classes from the design-system skill
- Use existing components from `@/components/ui`
- Use `gap` for spacing, not margins between siblings
- Match the visual hierarchy from the reference

### Step 4: Add to home page

Update `src/app/page.tsx` to include a link to the new prototype page.

### Step 5: Build new components if needed

If any element in the design doesn't have an existing component:
1. Build it using the add-component workflow
2. Then use it in the prototype page

### Step 6: Verify

Run `npm run build` to confirm everything compiles.
Open the page in dev mode to visually verify.

### Step 7: Report back

Tell the user:
- What page was created and its URL path
- What existing components were reused
- What new components were created (if any)
- Any compromises made vs. the reference design
