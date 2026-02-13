#!/usr/bin/env python3
"""
Feedback Triage - Categorize and prioritize customer feedback at scale.

Supports: Intercom, Zendesk, App Store, NPS surveys, generic CSV/JSON.
"""

import argparse
import csv
import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from collections import defaultdict

import yaml


@dataclass
class FeedbackEntry:
    text: str
    source: str = ""
    date: Optional[str] = None
    customer_segment: Optional[str] = None
    rating: Optional[int] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class TriagedFeedback:
    entries: list[FeedbackEntry] = field(default_factory=list)
    categories: dict = field(default_factory=dict)
    urgent: list[FeedbackEntry] = field(default_factory=list)
    focus_matches: list[FeedbackEntry] = field(default_factory=list)
    opportunities: list[FeedbackEntry] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


# Default theme keywords
THEME_PATTERNS = {
    'usability': [
        r'\bconfus', r'\bhard to', r'\bdifficult', r'\bcan\'t find', r'\bwhere is',
        r'\bnot intuitive', r'\bclunky', r'\bawkward', r'\bfrustrat', r'\bunclear'
    ],
    'performance': [
        r'\bslow', r'\blag', r'\bfreeze', r'\bcrash', r'\bbug', r'\berror',
        r'\bdoesn\'t load', r'\btimeout', r'\bbroken', r'\bglitch'
    ],
    'feature_request': [
        r'\bwish', r'\bwould be nice', r'\bplease add', r'\bneed.{0,20}feature',
        r'\bshould have', r'\bwant to be able', r'\bmissing', r'\bcan\'t do'
    ],
    'pricing': [
        r'\bexpensive', r'\bpric', r'\bcost', r'\bworth', r'\bpay', r'\bsubscri',
        r'\bfree', r'\btrial', r'\brefund', r'\bmoney'
    ],
    'onboarding': [
        r'\bget started', r'\bsetup', r'\bset up', r'\bfirst time', r'\bnew user',
        r'\blearning curve', r'\btutorial', r'\bonboard', r'\bsign.?up'
    ],
    'support': [
        r'\bsupport', r'\bhelp', r'\bresponse time', r'\bcustomer service',
        r'\bticket', r'\bno one', r'\bwaiting', r'\bunhelpful'
    ],
    'positive': [
        r'\blove', r'\bgreat', r'\bamazing', r'\bawesome', r'\bexcellent',
        r'\bfantastic', r'\bhelpful', r'\beasy', r'\bsimple', r'\bperfect'
    ],
}

# Urgency indicators
URGENCY_PATTERNS = [
    r'\bcancel', r'\bchurn', r'\bleaving', r'\bswitch', r'\bcompetitor',
    r'\bunacceptable', r'\bfurious', r'\bwaste', r'\bregret', r'\bterrible',
    r'\bhate', r'\bworst', r'\bawful', r'\bdisaster', r'\bfraud', r'\bscam',
    r'\bbroken', r'\burgent', r'\basap', r'\bimmediately', r'\bcritical'
]

# Opportunity indicators
OPPORTUNITY_PATTERNS = [
    r'\bwould pay', r'\bwilling to pay', r'\bupgrade', r'\bmore users',
    r'\bteam', r'\bcompany.wide', r'\brecommend', r'\btell.{0,10}friend',
    r'\bshare', r'\bexpand'
]


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def detect_format(file_path: str, content: str = None) -> str:
    """Detect the feedback source format."""
    ext = Path(file_path).suffix.lower()
    
    if ext == '.json':
        return 'json'
    
    if ext == '.csv':
        # Try to detect specific platforms from headers
        with open(file_path, 'r', encoding='utf-8') as f:
            header = f.readline().lower()
            
        if 'intercom' in header or 'conversation_id' in header:
            return 'intercom'
        if 'zendesk' in header or 'ticket_id' in header:
            return 'zendesk'
        if 'app store' in header or 'review_text' in header or 'store_review' in header:
            return 'appstore'
        if 'nps' in header or 'score' in header:
            return 'nps'
        return 'csv'
    
    if ext == '.txt':
        return 'text'
    
    return 'csv'  # default


def parse_feedback(file_path: str, format: str = None) -> list[FeedbackEntry]:
    """Parse feedback from various formats."""
    if format is None:
        format = detect_format(file_path)
    
    entries = []
    
    if format == 'json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    text = item.get('text') or item.get('feedback') or item.get('comment') or item.get('message', '')
                    if text:
                        entries.append(FeedbackEntry(
                            text=text,
                            source=item.get('source', ''),
                            date=item.get('date'),
                            customer_segment=item.get('segment'),
                            rating=item.get('rating'),
                            metadata=item
                        ))
    
    elif format == 'text':
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(FeedbackEntry(text=line))
    
    else:  # CSV formats
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Try common column names for feedback text
                text = None
                for col in ['feedback', 'comment', 'text', 'message', 'review', 
                           'review_text', 'body', 'content', 'description', 'notes']:
                    if col in row and row[col]:
                        text = row[col]
                        break
                
                if not text:
                    # Take first non-empty long text field
                    for key, val in row.items():
                        if val and len(str(val)) > 50:
                            text = val
                            break
                
                if text:
                    # Try to get other fields
                    segment = row.get('segment') or row.get('plan') or row.get('tier')
                    rating = row.get('rating') or row.get('score') or row.get('nps')
                    date = row.get('date') or row.get('created_at') or row.get('timestamp')
                    
                    entries.append(FeedbackEntry(
                        text=str(text),
                        source=row.get('source', format),
                        date=date,
                        customer_segment=segment,
                        rating=int(rating) if rating and str(rating).isdigit() else None,
                        metadata=row
                    ))
    
    return entries


def categorize_entry(entry: FeedbackEntry, custom_themes: dict = None) -> list[str]:
    """Assign categories to a feedback entry."""
    text = entry.text.lower()
    categories = []
    
    themes = THEME_PATTERNS.copy()
    if custom_themes:
        themes.update(custom_themes)
    
    for category, patterns in themes.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                categories.append(category)
                break
    
    if not categories:
        categories.append('uncategorized')
    
    return categories


def check_urgency(entry: FeedbackEntry, custom_keywords: list = None) -> bool:
    """Check if feedback indicates urgency."""
    text = entry.text.lower()
    
    patterns = URGENCY_PATTERNS.copy()
    if custom_keywords:
        patterns.extend([rf'\b{kw}' for kw in custom_keywords])
    
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # Low ratings are urgent
    if entry.rating is not None and entry.rating <= 2:
        return True
    
    return False


def check_opportunity(entry: FeedbackEntry) -> bool:
    """Check if feedback indicates expansion opportunity."""
    text = entry.text.lower()
    
    for pattern in OPPORTUNITY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # High ratings with substantive feedback
    if entry.rating is not None and entry.rating >= 4 and len(entry.text) > 100:
        return True
    
    return False


def check_focus_match(entry: FeedbackEntry, focus_areas: list) -> bool:
    """Check if feedback matches configured focus areas."""
    if not focus_areas:
        return False
    
    text = entry.text.lower()
    
    for focus in focus_areas:
        if focus.lower() in text:
            return True
    
    return False


def triage_feedback(entries: list[FeedbackEntry], config: dict = None) -> TriagedFeedback:
    """Triage all feedback entries."""
    result = TriagedFeedback()
    result.entries = entries
    result.categories = defaultdict(list)
    
    config = config or {}
    focus_areas = config.get('focus_areas', [])
    urgency_keywords = config.get('urgency_keywords', [])
    custom_themes = config.get('custom_themes', {})
    
    for entry in entries:
        # Categorize
        categories = categorize_entry(entry, custom_themes)
        for cat in categories:
            result.categories[cat].append(entry)
        
        # Check urgency
        if check_urgency(entry, urgency_keywords):
            result.urgent.append(entry)
        
        # Check focus match
        if check_focus_match(entry, focus_areas):
            result.focus_matches.append(entry)
        
        # Check opportunity
        if check_opportunity(entry):
            result.opportunities.append(entry)
    
    # Calculate stats
    result.stats = {
        'total': len(entries),
        'categories': {k: len(v) for k, v in result.categories.items()},
        'urgent_count': len(result.urgent),
        'focus_matches_count': len(result.focus_matches),
        'opportunities_count': len(result.opportunities),
    }
    
    return result


def format_output(triaged: TriagedFeedback, format: str = 'md', focus_areas: list = None) -> str:
    """Format triaged feedback for output."""
    
    if format == 'json':
        return json.dumps({
            'stats': triaged.stats,
            'categories': {k: [e.text for e in v] for k, v in triaged.categories.items()},
            'urgent': [e.text for e in triaged.urgent],
            'focus_matches': [e.text for e in triaged.focus_matches],
            'opportunities': [e.text for e in triaged.opportunities],
        }, indent=2)
    
    if format == 'csv':
        lines = ['category,urgency,text']
        for cat, entries in triaged.categories.items():
            for entry in entries:
                is_urgent = entry in triaged.urgent
                text = entry.text.replace('"', '""')[:200]
                lines.append(f'{cat},{"HIGH" if is_urgent else "normal"},"{text}"')
        return '\n'.join(lines)
    
    # Markdown format
    lines = []
    lines.append('# Feedback Triage Report')
    lines.append(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines.append(f'Total entries analyzed: {triaged.stats["total"]}')
    lines.append('')
    
    # Executive summary
    lines.append('## Executive Summary')
    lines.append('')
    
    # Top categories
    sorted_cats = sorted(triaged.stats['categories'].items(), key=lambda x: x[1], reverse=True)
    top_cats = [f"{cat} ({count})" for cat, count in sorted_cats[:3] if cat != 'uncategorized']
    lines.append(f'**Top themes:** {", ".join(top_cats)}')
    lines.append(f'**Urgent items:** {triaged.stats["urgent_count"]}')
    lines.append(f'**Opportunities identified:** {triaged.stats["opportunities_count"]}')
    lines.append('')
    
    # Focus area matches
    if focus_areas and triaged.focus_matches:
        lines.append('## Focus Area Matches')
        lines.append(f'*Feedback relevant to: {", ".join(focus_areas)}*')
        lines.append('')
        for entry in triaged.focus_matches[:10]:
            lines.append(f'- "{entry.text[:200]}..."' if len(entry.text) > 200 else f'- "{entry.text}"')
        if len(triaged.focus_matches) > 10:
            lines.append(f'- *...and {len(triaged.focus_matches) - 10} more*')
        lines.append('')
    
    # Urgent items
    if triaged.urgent:
        lines.append('## 🚨 Urgent Items')
        lines.append('*High frustration, churn risk, or critical issues*')
        lines.append('')
        for entry in triaged.urgent[:10]:
            lines.append(f'- "{entry.text[:200]}..."' if len(entry.text) > 200 else f'- "{entry.text}"')
        if len(triaged.urgent) > 10:
            lines.append(f'- *...and {len(triaged.urgent) - 10} more*')
        lines.append('')
    
    # Categories
    lines.append('## By Category')
    lines.append('')
    
    for cat, entries in sorted(triaged.categories.items(), key=lambda x: len(x[1]), reverse=True):
        if cat == 'uncategorized' and len(entries) < 3:
            continue
        
        lines.append(f'### {cat.replace("_", " ").title()} ({len(entries)} entries)')
        
        # Show representative quotes
        lines.append('Representative quotes:')
        for entry in entries[:5]:
            lines.append(f'- "{entry.text[:150]}..."' if len(entry.text) > 150 else f'- "{entry.text}"')
        if len(entries) > 5:
            lines.append(f'- *...and {len(entries) - 5} more*')
        lines.append('')
    
    # Opportunities
    if triaged.opportunities:
        lines.append('## 💡 Opportunities')
        lines.append('*Expansion signals, positive feedback with insights*')
        lines.append('')
        for entry in triaged.opportunities[:10]:
            lines.append(f'- "{entry.text[:200]}..."' if len(entry.text) > 200 else f'- "{entry.text}"')
        lines.append('')
    
    # LLM review prompt
    lines.append('---')
    lines.append('## Next Step: LLM Review')
    lines.append('Paste this report into Claude and ask for:')
    lines.append('1. Refined categories (merge similar, split overloaded)')
    lines.append('2. Themes the automated triage might have missed')
    lines.append('3. Recommended actions for top 3 themes')
    lines.append('4. Executive summary for stakeholders')
    
    return '\n'.join(lines)


def process_feedback(input_path: str, output_path: Optional[str] = None,
                     config_path: Optional[str] = None, focus_areas: list = None,
                     output_format: str = 'md', min_cluster: int = 2) -> str:
    """Process feedback file end-to-end."""
    
    # Load config
    config = {}
    if config_path:
        config = load_config(config_path)
    
    # Override focus areas if provided
    if focus_areas:
        config['focus_areas'] = focus_areas
    
    print(f"Loading feedback from: {input_path}")
    entries = parse_feedback(input_path)
    print(f"Loaded {len(entries)} entries")
    
    if not entries:
        return "No feedback entries found. Check your file format."
    
    # Triage
    triaged = triage_feedback(entries, config)
    print(f"Categorized into {len(triaged.categories)} themes")
    print(f"Found {triaged.stats['urgent_count']} urgent items")
    
    # Format output
    output = format_output(triaged, output_format, config.get('focus_areas'))
    
    # Determine output path
    if not output_path:
        input_p = Path(input_path)
        ext = 'json' if output_format == 'json' else 'csv' if output_format == 'csv' else 'md'
        output_path = str(input_p.with_suffix(f'.triaged.{ext}'))
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Triaged feedback saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Triage and categorize customer feedback at scale.'
    )
    parser.add_argument('input', help='Input feedback file (CSV, JSON, or TXT)')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--config', help='Path to config.yaml')
    parser.add_argument('--focus', help='Comma-separated focus areas')
    parser.add_argument('--format', choices=['md', 'json', 'csv'], default='md',
                        help='Output format (default: md)')
    parser.add_argument('--min-cluster', type=int, default=2,
                        help='Minimum entries for a theme (default: 2)')
    
    args = parser.parse_args()
    
    focus_areas = None
    if args.focus:
        focus_areas = [f.strip() for f in args.focus.split(',')]
    
    process_feedback(
        args.input,
        args.output,
        args.config,
        focus_areas,
        args.format,
        args.min_cluster
    )


if __name__ == '__main__':
    main()
