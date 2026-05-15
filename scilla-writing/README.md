# Scilla Writing

Writing styles for product management content: case studies and LinkedIn posts.

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

Install via the `scilla-studio` marketplace:

```
/plugin marketplace add scilla-studio-stockholm/claude-plugins
/plugin install scilla-writing@scilla-studio
```

## Usage

The skills activate automatically when Claude detects relevant triggers in your requests. You can also explicitly reference them:

```
"Write a case study for the Avanza project using scilla-writing:case-study"
"Create a LinkedIn post using scilla-writing:linkedin-post"
```
