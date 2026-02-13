# Joni's Writing Skills Plugin

Personal writing styles for case studies and LinkedIn posts.

## Skills Included

### 1. Case Study (`case-study`)
Activates when writing case studies or documenting client work for scilla.studio.

**Triggers:**
- "write a case study"
- "fallstudie"
- "scilla.studio case"
- "skriv ett case"
- documenting client work results and impact

**Style:** Direct, concrete, honest storytelling. Swedish language. Focus on real impact, not fluff.

### 2. LinkedIn Post (`linkedin-post`)
Activates when writing LinkedIn posts about product management insights.

**Triggers:**
- "write a LinkedIn post"
- "LinkedIn-inlägg"
- "skriv ett inlägg"
- "share an idea on LinkedIn"
- posting about product management insights

**Style:** Conversational, concrete with numbers, one universal insight per post. Swedish language. 10-20 lines max.

## Installation

Copy the plugin to your local plugins directory or reference it directly:

```bash
# Option 1: Symlink to Claude's plugins directory (if supported)
ln -s ~/claude-plugins/joni-writing ~/.claude/plugins/local/joni-writing

# Option 2: Use as reference when needed
# Just tell Claude to reference the skills in ~/claude-plugins/joni-writing/
```

## Usage

The skills activate automatically when Claude detects relevant triggers in your requests. You can also explicitly reference them:

```
"Write a case study for the Avanza project following my case-study skill"
"Create a LinkedIn post about this insight using my linkedin-post skill"
```
