---
name: design-system
description: "Use when building any prototype page, creating new components, or modifying UI in this project."
---

# [CLIENT_NAME] Design System Reference

## When to Use
Use when building any prototype page, creating new components, or modifying UI in this project.

---

## Color Tokens → Tailwind Classes

### Surfaces / Backgrounds
| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| surface | #FFFFFF | `bg-surface` | Default page/card background |
| surface-secondary | [GREY_100] | `bg-surface-secondary` | Subtle alternate background |
| surface-tertiary | [GREY_200] | `bg-surface-tertiary` | Disabled inputs, muted areas |
| surface-inverted | [GREY_800] | `bg-surface-inverted` | Dark backgrounds |
| accent | [ACCENT_HEX] | `bg-accent` | Primary buttons, active states |
| accent-surface | [BRAND_50] | `bg-accent-surface` | Light brand tint background |
| accent-fg | [ACCENT_FG_HEX] | `bg-accent-fg` | Rare — use for text/links instead |

### Text / Foreground
| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| foreground | [GREY_800] | `text-foreground` | Primary text (headings, body) |
| foreground-secondary | [GREY_500] | `text-foreground-secondary` | Inactive nav labels |
| foreground-tertiary | [GREY_600] | `text-foreground-tertiary` | Subtitles, metadata |
| foreground-muted | [GREY_400] | `text-foreground-muted` | Disabled text, placeholders |
| foreground-on-color | #FFFFFF | `text-foreground-on-color` | Text on colored backgrounds |
| accent-fg | [ACCENT_FG_HEX] | `text-accent-fg` | Links, text buttons, active tabs |

### Borders
| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| border | [GREY_200] | `border-border` | Default borders |
| border-accent | [ACCENT_HEX] | `border-border-accent` | Selected/focused borders |
| border-muted | [GREY_300] | `border-border-muted` | Disabled borders |

### Status Colors
| Token | Hex | Tailwind bg / text | Usage |
|-------|-----|-------------------|-------|
| positive | [POSITIVE] | `bg-positive` / `text-positive` | Success, available |
| positive-surface | [POSITIVE_SURFACE] | `bg-positive-surface` | Light green bg |
| negative | [NEGATIVE] | `bg-negative` / `text-negative` | Error, badges |
| negative-surface | [NEGATIVE_SURFACE] | `bg-negative-surface` | Light red bg |
| info | [INFO] | `bg-info` / `text-info` | Info states |
| info-surface | [INFO_SURFACE] | `bg-info-surface` | Light blue bg |
| warning | [WARNING] | `bg-warning` / `text-warning` | Warning states |
| warning-surface | [WARNING_SURFACE] | `bg-warning-surface` | Light yellow bg |

---

## Typography

Font: **[FONT_FAMILY]** (loaded via `next/font/google` in layout.tsx)

| Style | Weight | Size/LH | Tailwind classes |
|-------|--------|---------|-----------------|
[TYPOGRAPHY_ROWS]

---

## Border Radius

| Token | Value | Tailwind | Usage |
|-------|-------|----------|-------|
| xs | 8px | `rounded-xs` | Images in tiles |
| sm | 12px | `rounded-sm` | Small elements |
| md | 16px | `rounded-md` | List items, text fields, tiles |
| lg | 20px | `rounded-lg` | Cards, sheets |
| xl | 32px | `rounded-xl` | Large cards |
| full | 50px | `rounded-full` | Buttons, chips, pills, avatars |

---

## Shadows

| Token | Tailwind | Usage |
|-------|----------|-------|
| Small | `shadow-sm` | Hover states, avatars |
| Medium | `shadow-md` | Floating elements, list items |
| Large | `shadow-lg` | Cards, modals |
| Sheet | `shadow-sheet` | Bottom sheets |

---

## Component Library

Import from `@/components/ui`:

### MobileLayout
```tsx
<MobileLayout bg="bg-accent-surface">
  {/* page content */}
</MobileLayout>
```
Wraps content in a 375x812 phone frame for desktop viewing.

### TopNav + IconButton
```tsx
<TopNav
  title="Page Title"
  leftAction={<IconButton><BackIcon /></IconButton>}
  rightAction={<IconButton><BellIcon /></IconButton>}
  transparent={false}
/>
```

### BottomNav
```tsx
<BottomNav items={[
  { label: "Tab 1", icon: <Icon />, active: true },
  { label: "Tab 2", icon: <Icon /> },
]} />
```

---

## Page Structure

Every prototype page:
```tsx
"use client";
import { MobileLayout, TopNav, BottomNav } from "@/components/ui";

export default function MyPrototype() {
  return (
    <MobileLayout bg="bg-accent-surface">
      <TopNav title="Page Title" />
      <div className="flex flex-col gap-4 p-4">
        {/* content */}
      </div>
      <div className="mt-auto">
        <BottomNav items={[...]} />
      </div>
    </MobileLayout>
  );
}
```

---

## Figma Auto-Layout → Tailwind

| Figma Property | Tailwind |
|---------------|----------|
| Direction: Horizontal | `flex flex-row` |
| Direction: Vertical | `flex flex-col` |
| Gap: N px | `gap-N` (1=4px, 2=8px, 3=12px, 4=16px, 6=24px) |
| Align: Center | `items-center justify-center` |
| Resizing: Fill | `flex-1` |
| Resizing: Hug | `w-fit` / `h-fit` |
| Wrap | `flex-wrap` |
| Padding: 16px | `p-4` |
| Padding: 8px 16px | `px-4 py-2` |

---

## Rules

1. NEVER hardcode colors — always use semantic Tailwind classes from the token table above
2. NEVER use margin between siblings — use `gap` on the parent
3. ALWAYS import components from `@/components/ui`
4. ALWAYS wrap prototype pages in `<MobileLayout>`
5. When a design needs a component that doesn't exist, create it in `src/components/ui/` following existing patterns
6. Spacing follows a 4px grid
7. Use semantic color names (`bg-surface`, `text-foreground`) not raw values (`bg-white`, `text-gray-900`)
8. This is a mobile app — design for 375px width
9. Use [LOCALE] for placeholder content
