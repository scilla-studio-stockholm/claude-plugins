# Supported Input Formats

Reference for feedback sources the triage script can process.

## Intercom Exports

**How to export:**
1. Go to Intercom → Reports → Conversations
2. Export as CSV

**Expected columns:**
- `conversation_id`
- `message` or `body` (feedback text)
- `created_at`
- `user_id`
- `tags`

**Notes:**
- Script looks for `message`, `body`, or `content` columns for feedback text
- Customer segment pulled from `plan` or `segment` if available

---

## Zendesk Exports

**How to export:**
1. Go to Zendesk → Explore → Reports
2. Create ticket export with comments
3. Export as CSV

**Expected columns:**
- `ticket_id`
- `description` or `comment`
- `created_at`
- `priority`
- `tags`

**Notes:**
- High priority tickets auto-flagged as urgent
- Tags can be used for custom categorization

---

## App Store / Play Store Reviews

**How to get data:**
- App Store Connect → Reviews export
- Play Console → Reviews → Download
- Third-party tools: AppFollow, Appbot, Sensor Tower

**Expected columns:**
- `review_text` or `review`
- `rating` (1-5)
- `date`
- `version`
- `country`

**Notes:**
- Ratings 1-2 auto-flagged as urgent
- Ratings 4-5 with substantive text flagged as opportunities

---

## NPS Surveys

**Common export formats from:**
- Delighted
- Wootric
- SurveyMonkey
- Typeform

**Expected columns:**
- `score` or `nps` (0-10)
- `feedback` or `comment`
- `date`
- `segment` (if available)

**Notes:**
- Detractors (0-6) auto-flagged as urgent
- Promoters (9-10) with comments flagged as opportunities

---

## Generic CSV

Any CSV with a text column containing feedback will work.

**The script looks for these column names (in order):**
1. `feedback`
2. `comment`
3. `text`
4. `message`
5. `review`
6. `review_text`
7. `body`
8. `content`
9. `description`
10. `notes`

If none found, uses first column with >50 characters of text.

**Optional columns recognized:**
- `segment`, `plan`, `tier` → customer segment
- `rating`, `score`, `nps` → numeric rating
- `date`, `created_at`, `timestamp` → date
- `source` → feedback source

---

## JSON Format

```json
[
  {
    "text": "The onboarding was confusing",
    "date": "2024-01-15",
    "rating": 3,
    "segment": "trial",
    "source": "in-app survey"
  },
  {
    "feedback": "Love the new dashboard!",
    "rating": 5
  }
]
```

**Recognized text fields:** `text`, `feedback`, `comment`, `message`

---

## Plain Text

One feedback entry per line:

```
The checkout process is too slow
I wish there was a dark mode
Great product, but expensive for small teams
```

**Notes:**
- No metadata available
- Useful for quick triage of pasted feedback
