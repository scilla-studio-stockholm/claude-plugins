#!/usr/bin/env python3
"""
Competitive Intelligence Gatherer

Collects and structures public data from multiple sources for competitive analysis.
Uses Playwright for JavaScript-rendered pages (signup, checkout, app pages).
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict
from urllib.parse import urlparse, urljoin
import time

# Check for playwright availability
PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass


@dataclass
class CompetitorIntel:
    name: str
    url: str
    gathered_at: str = ""
    sources: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    return text


def fetch_url_curl(url: str, timeout: int = 30) -> Optional[str]:
    """Fetch URL content using curl (for static pages)."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', '-A',
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
             '--max-time', str(timeout),
             url],
            capture_output=True,
            text=True,
            timeout=timeout + 5
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def fetch_url_playwright(url: str, timeout: int = 30000, wait_for_selector: str = None, click_monthly: bool = False) -> Optional[str]:
    """Fetch URL content using Playwright (for JS-rendered pages)."""
    if not PLAYWRIGHT_AVAILABLE:
        print("  ⚠️  Playwright not available, falling back to curl")
        return fetch_url_curl(url, timeout // 1000)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = context.new_page()
            page.goto(url, timeout=timeout)

            # Wait for network to be idle (JS to finish loading)
            page.wait_for_load_state('networkidle', timeout=timeout)

            # Optionally wait for specific selector
            if wait_for_selector:
                try:
                    page.wait_for_selector(wait_for_selector, timeout=5000)
                except:
                    pass

            # For pricing pages, try to click "Monthly" toggle to see non-discounted prices
            if click_monthly:
                try:
                    monthly_btn = page.locator('text=Monthly').first
                    monthly_btn.click()
                    page.wait_for_timeout(2000)
                except:
                    pass  # Toggle may not exist

            # Get rendered HTML
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        print(f"  Error fetching {url} with Playwright: {e}")
        return None


def fetch_url(url: str, timeout: int = 30, use_browser: bool = False, click_monthly: bool = False) -> Optional[str]:
    """Fetch URL content - uses Playwright for JS pages, curl otherwise."""
    if use_browser:
        return fetch_url_playwright(url, timeout * 1000, click_monthly=click_monthly)
    return fetch_url_curl(url, timeout)


def extract_text_from_html(html: str) -> str:
    """Extract readable text from HTML."""
    if not html:
        return ""

    # Remove script and style elements
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

    # Replace common block elements with newlines
    html = re.sub(r'</(p|div|h[1-6]|li|tr|br)[^>]*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<(br|hr)[^>]*/?\s*>', '\n', html, flags=re.IGNORECASE)

    # Remove remaining HTML tags
    html = re.sub(r'<[^>]+>', ' ', html)

    # Decode common HTML entities
    html = html.replace('&nbsp;', ' ')
    html = html.replace('&amp;', '&')
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&quot;', '"')
    html = html.replace('&#39;', "'")
    html = html.replace('&rsquo;', "'")
    html = html.replace('&lsquo;', "'")
    html = html.replace('&rdquo;', '"')
    html = html.replace('&ldquo;', '"')
    html = html.replace('&mdash;', '—')
    html = html.replace('&ndash;', '–')

    # Clean up whitespace
    html = re.sub(r'\n\s*\n', '\n\n', html)
    html = re.sub(r' +', ' ', html)

    lines = [line.strip() for line in html.split('\n') if line.strip()]

    return '\n'.join(lines)


def extract_links(html: str, base_url: str) -> list[str]:
    """Extract all links from HTML."""
    links = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)

    full_links = []
    for link in links:
        if link.startswith('http'):
            full_links.append(link)
        elif link.startswith('/'):
            full_links.append(urljoin(base_url, link))

    return list(set(full_links))


def find_page_url(links: list[str], keywords: list[str]) -> Optional[str]:
    """Find a URL containing any of the keywords."""
    for link in links:
        link_lower = link.lower()
        for keyword in keywords:
            if keyword in link_lower:
                return link
    return None


def find_signup_url(base_url: str, links: list[str]) -> Optional[str]:
    """Find signup/checkout URL - check common patterns."""
    # Common signup URL patterns
    signup_patterns = [
        'signup', 'sign-up', 'register', 'pricing', 'checkout',
        'subscribe', 'get-started', 'start', 'trial', 'buy'
    ]

    # First check links found on the page
    for link in links:
        link_lower = link.lower()
        for pattern in signup_patterns:
            if pattern in link_lower and ('app.' in link_lower or '/auth/' in link_lower or '/signup' in link_lower):
                return link

    # Try common app subdomain patterns
    parsed = urlparse(base_url)
    domain = parsed.netloc.replace('www.', '')

    common_signup_urls = [
        f"https://app.{domain}/signup",
        f"https://app.{domain}/auth/signup",
        f"https://app.{domain}/auth/signup-payment",
        f"https://app.{domain}/register",
        f"https://{domain}/signup",
        f"https://{domain}/app/signup",
    ]

    return common_signup_urls


def gather_actual_pricing(intel: CompetitorIntel, output_dir: Path):
    """
    Gather ACTUAL pricing from signup/checkout flow.
    Marketing /pricing pages often differ from real checkout prices.
    """
    print(f"\n💰 Gathering actual pricing from signup flow...")

    raw_dir = output_dir / "raw"
    base_url = intel.url.rstrip('/')
    parsed = urlparse(base_url)
    domain = parsed.netloc.replace('www.', '')

    # Try common signup URL patterns
    signup_urls = [
        f"https://app.{domain}/signup",
        f"https://app.{domain}/auth/signup",
        f"https://app.{domain}/auth/signup-payment",
        f"https://app.{domain}/register",
        f"https://app.{domain}/pricing",
        f"https://{domain}/signup",
        f"https://{domain}/app/signup",
    ]

    for signup_url in signup_urls:
        print(f"  Trying {signup_url}...")
        html = fetch_url(signup_url, timeout=45, use_browser=True)
        if html:
            text = extract_text_from_html(html)
            # Check if we got actual content (not just a redirect or error)
            if len(text) > 500 and ('$' in text or 'price' in text.lower() or 'plan' in text.lower()):
                (raw_dir / "pricing_actual.md").write_text(
                    f"# Actual Pricing (from Signup Flow)\nSource: {signup_url}\n\n"
                    f"⚠️ NOTE: This is from the actual signup/checkout flow, which may differ from the marketing /pricing page.\n\n"
                    f"{text}"
                )
                intel.sources['pricing_actual'] = {'url': signup_url, 'length': len(text)}
                intel.metadata['pricing_source'] = 'signup_flow'
                print(f"  ✅ Found actual pricing at {signup_url}")
                return

    print("  ⚠️  Could not access signup flow - pricing may only reflect marketing page")
    intel.metadata['pricing_source'] = 'marketing_page_only'
    intel.metadata['pricing_warning'] = 'Could not verify actual checkout pricing'


def gather_website(intel: CompetitorIntel, output_dir: Path):
    """Gather data from main website."""
    print(f"\n📡 Gathering website data from {intel.url}")

    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    base_url = intel.url.rstrip('/')

    # Fetch homepage
    print("  Fetching homepage...")
    homepage_html = fetch_url(base_url)
    if homepage_html:
        homepage_text = extract_text_from_html(homepage_html)
        (raw_dir / "homepage.md").write_text(f"# Homepage\nSource: {base_url}\n\n{homepage_text}")
        intel.sources['homepage'] = {'url': base_url, 'length': len(homepage_text)}

        # Extract links for finding other pages
        links = extract_links(homepage_html, base_url)
        intel.metadata['links_found'] = len(links)

        # Try to find key pages
        pages_to_find = {
            'pricing': ['pricing', 'plans', 'packages'],
            'about': ['about', 'company', 'team', 'story'],
            'careers': ['careers', 'jobs', 'hiring', 'work-with-us'],
            'customers': ['customers', 'case-studies', 'testimonials', 'stories'],
            'changelog': ['changelog', 'releases', 'updates', 'whats-new', "what's-new"],
            'features': ['features', 'product', 'solutions', 'platform'],
            'integrations': ['integrations', 'apps', 'partners', 'ecosystem'],
            'docs': ['docs', 'documentation', 'help', 'support', 'guides'],
        }

        for page_name, keywords in pages_to_find.items():
            page_url = find_page_url(links, keywords)
            if page_url:
                print(f"  Fetching {page_name}...")
                time.sleep(1)  # Be polite
                # Use browser for pricing page - it often renders differently via JS
                # Also click "Monthly" toggle to capture true monthly pricing (not annual)
                use_browser = (page_name == 'pricing')
                click_monthly = (page_name == 'pricing')
                page_html = fetch_url(page_url, use_browser=use_browser, click_monthly=click_monthly)
                if page_html:
                    page_text = extract_text_from_html(page_html)
                    note = ""
                    if page_name == 'pricing':
                        note = "\n\n⚠️ NOTE: Captured with 'Monthly' billing toggle selected (if available). Many SaaS sites default to showing discounted annual pricing.\n"
                    (raw_dir / f"{page_name}.md").write_text(
                        f"# {page_name.title()}\nSource: {page_url}{note}\n\n{page_text}"
                    )
                    intel.sources[page_name] = {'url': page_url, 'length': len(page_text)}
    else:
        print("  ❌ Could not fetch homepage")


def gather_changelog(intel: CompetitorIntel, changelog_url: str, output_dir: Path):
    """Gather changelog/release notes."""
    print(f"\n📋 Gathering changelog from {changelog_url}")

    raw_dir = output_dir / "raw"

    html = fetch_url(changelog_url)
    if html:
        text = extract_text_from_html(html)
        (raw_dir / "changelog.md").write_text(f"# Changelog\nSource: {changelog_url}\n\n{text}")
        intel.sources['changelog'] = {'url': changelog_url, 'length': len(text)}

        # Try to extract dates and entries
        date_pattern = r'\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2}|\w+ \d{1,2},? 20\d{2})\b'
        dates = re.findall(date_pattern, text)
        intel.metadata['changelog_dates_found'] = len(dates)
        if dates:
            intel.metadata['changelog_latest'] = dates[0]
    else:
        print("  ❌ Could not fetch changelog")


def gather_careers(intel: CompetitorIntel, careers_url: str, output_dir: Path):
    """Gather job postings."""
    print(f"\n💼 Gathering careers from {careers_url}")

    raw_dir = output_dir / "raw"

    html = fetch_url(careers_url)
    if html:
        text = extract_text_from_html(html)
        (raw_dir / "careers.md").write_text(f"# Careers/Job Postings\nSource: {careers_url}\n\n{text}")
        intel.sources['careers'] = {'url': careers_url, 'length': len(text)}

        # Try to count job categories
        job_keywords = {
            'engineering': ['engineer', 'developer', 'software', 'backend', 'frontend', 'devops', 'sre'],
            'product': ['product manager', 'product design', 'ux', 'ui'],
            'sales': ['sales', 'account executive', 'business development', 'bdr', 'sdr'],
            'marketing': ['marketing', 'growth', 'content', 'brand'],
            'support': ['support', 'success', 'customer'],
            'data': ['data', 'analytics', 'machine learning', 'ai'],
        }

        text_lower = text.lower()
        job_counts = {}
        for category, keywords in job_keywords.items():
            count = sum(text_lower.count(kw) for kw in keywords)
            if count > 0:
                job_counts[category] = count

        intel.metadata['job_categories'] = job_counts
    else:
        print("  ❌ Could not fetch careers page")


def gather_reviews_g2(intel: CompetitorIntel, g2_url: str, output_dir: Path):
    """Gather G2 reviews."""
    print(f"\n⭐ Gathering G2 reviews from {g2_url}")

    raw_dir = output_dir / "raw"

    # G2 requires browser rendering
    html = fetch_url(g2_url, use_browser=True)
    if html:
        text = extract_text_from_html(html)
        (raw_dir / "reviews_g2.md").write_text(f"# G2 Reviews\nSource: {g2_url}\n\n{text}")
        intel.sources['reviews_g2'] = {'url': g2_url, 'length': len(text)}
    else:
        print("  ❌ Could not fetch G2 reviews")


def gather_reviews_appstore(intel: CompetitorIntel, appstore_url: str, output_dir: Path):
    """Gather App Store reviews."""
    print(f"\n📱 Gathering App Store reviews from {appstore_url}")

    raw_dir = output_dir / "raw"

    html = fetch_url(appstore_url)
    if html:
        text = extract_text_from_html(html)
        (raw_dir / "reviews_appstore.md").write_text(f"# App Store Reviews\nSource: {appstore_url}\n\n{text}")
        intel.sources['reviews_appstore'] = {'url': appstore_url, 'length': len(text)}
    else:
        print("  ❌ Could not fetch App Store reviews")


def generate_summary(intel: CompetitorIntel, output_dir: Path):
    """Generate summary of gathered data."""
    print("\n📊 Generating summary...")

    summary_lines = [
        f"# Competitive Intel: {intel.name}",
        f"Gathered: {intel.gathered_at}",
        f"Base URL: {intel.url}",
        "",
        "## Data Collected",
        ""
    ]

    for source, info in intel.sources.items():
        summary_lines.append(f"- **{source}**: {info.get('length', 0):,} chars from {info.get('url', 'N/A')}")

    summary_lines.extend([
        "",
        "## Metadata",
        ""
    ])

    for key, value in intel.metadata.items():
        summary_lines.append(f"- **{key}**: {value}")

    # Add pricing warning if applicable
    if intel.metadata.get('pricing_warning'):
        summary_lines.extend([
            "",
            "## ⚠️ Pricing Warning",
            "",
            intel.metadata['pricing_warning'],
            "Marketing page pricing may not reflect actual checkout prices.",
        ])

    summary_lines.extend([
        "",
        "## Files Ready for Analysis",
        ""
    ])

    raw_dir = output_dir / "raw"
    if raw_dir.exists():
        for f in sorted(raw_dir.iterdir()):
            if f.suffix == '.md':
                summary_lines.append(f"- `raw/{f.name}`")

    (output_dir / "summary.md").write_text('\n'.join(summary_lines))

    # Save metadata JSON
    (output_dir / "raw" / "metadata.json").write_text(json.dumps(asdict(intel), indent=2))


def main():
    parser = argparse.ArgumentParser(
        description='Gather competitive intelligence from public sources.'
    )
    parser.add_argument('name', help='Competitor name')
    parser.add_argument('--url', required=True, help='Competitor website URL')
    parser.add_argument('--changelog', help='Changelog/release notes URL')
    parser.add_argument('--careers', help='Careers page URL')
    parser.add_argument('--g2', help='G2 reviews URL')
    parser.add_argument('--appstore', help='App Store URL')
    parser.add_argument('--signup', help='Signup/checkout URL for actual pricing')
    parser.add_argument('--skip-pricing-check', action='store_true',
                        help='Skip checking actual pricing from signup flow')
    parser.add_argument('--output', '-o', help='Output directory (default: ./output/company_name)')

    args = parser.parse_args()

    # Check playwright availability
    if not PLAYWRIGHT_AVAILABLE:
        print("⚠️  Playwright not installed. Some JS-rendered pages may not be captured.")
        print("   Install with: pip install playwright && playwright install chromium")
        print("")

    # Setup
    intel = CompetitorIntel(
        name=args.name,
        url=args.url,
        gathered_at=datetime.now().isoformat()
    )

    slug = slugify(args.name)
    output_dir = Path(args.output) if args.output else Path(f"./output/{slug}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🔍 Starting competitive teardown for: {args.name}")
    print(f"   Output directory: {output_dir}")

    # Gather from each source
    gather_website(intel, output_dir)

    # IMPORTANT: Check actual pricing from signup flow
    if not args.skip_pricing_check:
        gather_actual_pricing(intel, output_dir)

    if args.changelog:
        gather_changelog(intel, args.changelog, output_dir)

    if args.careers:
        gather_careers(intel, args.careers, output_dir)

    if args.g2:
        gather_reviews_g2(intel, args.g2, output_dir)

    if args.appstore:
        gather_reviews_appstore(intel, args.appstore, output_dir)

    # Generate summary
    generate_summary(intel, output_dir)

    print(f"\n✅ Data gathering complete!")
    print(f"   Sources collected: {len(intel.sources)}")
    print(f"   Summary: {output_dir}/summary.md")

    if intel.metadata.get('pricing_warning'):
        print(f"\n⚠️  PRICING WARNING: {intel.metadata['pricing_warning']}")

    print(f"\n   Next: Run LLM analysis with references/analysis_prompt.md")


if __name__ == '__main__':
    main()
