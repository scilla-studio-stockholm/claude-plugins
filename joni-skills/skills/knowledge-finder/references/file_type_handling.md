# File Type Handling Reference

How the Knowledge Finder extracts and tracks content from different research file types.

## Supported File Types

| Extension | Type | Location Tracking | Speaker Detection |
|-----------|------|-------------------|-------------------|
| .txt, .md | Plain text/Markdown | Line number | Yes |
| .docx | Word document | Paragraph number, Table/Row/Col | Yes |
| .pdf | PDF document | Page number, Paragraph, Table/Row/Col | No |
| .xlsx, .xls | Excel spreadsheet | Sheet name, Row, Column header | No |
| .csv, .tsv | Delimited data | Row, Column header | No |
| .json | JSON data | JSON path (dot notation) | No |
| .html, .htm | HTML document | Element index, Tag type | No |

---

## Location Tracking by Type

### Text Files (.txt, .md)

**Location format:** `Line {n}`

**Speaker detection patterns:**
- `Speaker 1:` / `Speaker 2:`
- `P1:` / `P2:` / `Participant 1:`
- `Interviewer:` / `Moderator:`
- `[Speaker Name]:`
- `**Speaker Name**:`
- `John Smith:` (capitalized name followed by colon)

**Example output:**
```json
{
  "content": "The onboarding was really confusing at first",
  "location": "Line 47",
  "speaker": "P3",
  "context_before": "Interviewer: How was your first experience?",
  "context_after": "I didn't know where to click."
}
```

### Word Documents (.docx)

**Location format:** 
- Body text: `Paragraph {n}`
- Tables: `Table {n}, Row {r}, Col {c}`

**Extracts from:**
- All paragraphs (with style info)
- All table cells

**Example output:**
```json
{
  "content": "Key finding: Users struggle with navigation",
  "location": "Paragraph 12",
  "style": "Heading 2"
}
```

### PDF Documents (.pdf)

**Location format:**
- Body text: `Page {n}, Paragraph {p}`
- Tables: `Page {n}, Table {t}, Row {r}, Col {c}`

**Notes:**
- Uses pdfplumber for extraction
- Quality depends on PDF structure (scanned PDFs may extract poorly)
- Tables are extracted separately from body text

**Example output:**
```json
{
  "content": "72% of respondents reported difficulty with checkout",
  "location": "Page 5, Paragraph 3",
  "page_number": 5
}
```

### Excel Spreadsheets (.xlsx, .xls)

**Location format:** `Sheet "{name}", Row {n}, Column "{header}"`

**Extraction behavior:**
- First row treated as headers
- Column headers used in location for clarity
- All sheets processed
- Empty cells skipped

**Example output:**
```json
{
  "content": "Frustrated with lack of documentation",
  "location": "Sheet \"Interview Notes\", Row 15, Column \"Pain Points\"",
  "sheet": "Interview Notes",
  "row": 15,
  "column_header": "Pain Points"
}
```

### CSV/TSV Files (.csv, .tsv)

**Location format:** `Row {n}, Column "{header}"`

**Extraction behavior:**
- Auto-detects delimiter
- First row treated as headers
- Handles quoted fields

**Example output:**
```json
{
  "content": "Would definitely recommend to a colleague",
  "location": "Row 234, Column \"NPS Comment\"",
  "row": 234,
  "column_header": "NPS Comment"
}
```

### JSON Files (.json)

**Location format:** `Path: {dot.notation.path}`

**Extraction behavior:**
- Recursively extracts all string values
- Tracks full path using dot notation
- Array indices shown as `[n]`

**Example output:**
```json
{
  "content": "The API documentation was incomplete",
  "location": "Path: responses[3].feedback.comment",
  "json_path": "responses[3].feedback.comment"
}
```

### HTML Files (.html, .htm)

**Location format:** `Element {n} ({tag})`

**Extraction behavior:**
- Strips script and style tags
- Preserves text content only
- Tracks element index and tag type

---

## Date Detection

The script attempts to detect research dates from multiple sources (in priority order):

1. **Filename patterns:**
   - `2024-01-15` or `2024_01_15`
   - `15-01-2024` or `15_01_2024`
   - `20240115`
   - `Q1 2024` or `Q1-2024`
   - `January 2024` or `January-2024`

2. **Content patterns:** Same patterns searched in first 10 segments

3. **File modification date:** Fallback to filesystem metadata

---

## Handling Large Files

For files with many segments:
- All segments are searched (no sampling)
- Results sorted by match score
- Context limited to 200 characters before/after

---

## Error Handling

If a file cannot be processed:
- Error logged in `extraction_errors` array
- File still appears in results with zero evidence
- Search continues with remaining files

**Common errors:**
- Missing dependencies (python-docx, pdfplumber, openpyxl)
- Corrupted files
- Password-protected files
- Encoding issues (handled with replacement characters)

---

## Dependencies

Required Python packages:
```bash
pip install python-docx pdfplumber openpyxl
```

Built-in modules used: csv, json, html.parser
