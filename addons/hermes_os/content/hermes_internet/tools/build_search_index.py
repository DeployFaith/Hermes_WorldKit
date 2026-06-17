#!/usr/bin/env python3
"""Build static search index for pythia.com from WorldWeb content."""

from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registry.json"
OUTPUT_PATH = REPO_ROOT / "sites" / "pythia.com" / "data" / "search-index.json"
AGORA_LISTINGS_PATH = REPO_ROOT / "apps" / "agora-market" / "src" / "listings.js"

TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
WHITESPACE_RE = re.compile(r"\s+")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
META_RE = re.compile(r"<meta\s+[^>]*>", re.IGNORECASE)
ATTR_RE = re.compile(r"([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*([\"'])(.*?)\2", re.DOTALL)
HEADING_RE = re.compile(r"<h[1-3][^>]*>(.*?)</h[1-3]>", re.IGNORECASE | re.DOTALL)


def clean_text(raw: str) -> str:
    text = SCRIPT_STYLE_RE.sub(" ", raw)
    text = TAG_RE.sub(" ", text)
    text = unescape(text)
    return WHITESPACE_RE.sub(" ", text).strip()


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def snippet_from_html(html: str, fallback: str) -> str:
    text = clean_text(html)
    if not text:
        return fallback
    return text[:220]


def extract_title(html: str, fallback: str) -> str:
    match = TITLE_RE.search(html)
    if not match:
        return fallback
    title = clean_text(match.group(1))
    return title or fallback


def extract_meta_content(html: str, key: str) -> str:
    key = key.lower()
    for tag in META_RE.findall(html):
        attrs = {k.lower(): v for k, _, v in ATTR_RE.findall(tag)}
        name = attrs.get("name", "").lower()
        prop = attrs.get("property", "").lower()
        if name == key or prop == key:
            return clean_text(attrs.get("content", ""))
    return ""


def extract_headings(html: str) -> list[str]:
    headings: list[str] = []
    for match in HEADING_RE.findall(html):
        heading = clean_text(match)
        if heading:
            headings.append(heading)
    return headings[:8]


def body_from_html(html: str) -> str:
    return clean_text(html)[:1200]


def load_agora_listings() -> list[dict]:
    raw = AGORA_LISTINGS_PATH.read_text(encoding="utf-8")
    array_match = re.search(r"\[(.*)\]", raw, re.DOTALL)
    if array_match is None:
        return []
    js_array = "[" + array_match.group(1) + "]"
    normalized = re.sub(r"([\{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', js_array)
    normalized = normalized.replace("'", '"')
    try:
        parsed = json.loads(normalized)
    except json.JSONDecodeError:
        return []
    return [item for item in parsed if isinstance(item, dict)]


def build_index() -> dict:
    registry = load_registry()
    sites = registry.get("sites", [])
    entries: list[dict] = []

    for site in sites:
        if not isinstance(site, dict):
            continue
        domain = str(site.get("domain", "")).strip()
        title = str(site.get("title", domain)).strip() or domain
        description = str(site.get("description", "")).strip()
        root = str(site.get("root", "")).strip()
        routes = site.get("routes", {})

        if not domain or not root:
            continue

        site_json_path = REPO_ROOT / root / "site.json"
        keywords: list[str] = []
        if site_json_path.exists():
            try:
                site_json = json.loads(site_json_path.read_text(encoding="utf-8"))
                value = site_json.get("keywords")
                if isinstance(value, list):
                    keywords = [str(item).strip() for item in value if str(item).strip()]
            except json.JSONDecodeError:
                pass

        site_keywords = [item for item in [domain, title, description, *keywords] if item]

        entries.append(
            {
                "type": "Site",
                "domain": domain,
                "url": f"https://{domain}/",
                "canonical_url": f"https://{domain}/",
                "title": title,
                "description": description,
                "snippet": description,
                "headings": [],
                "body": description,
                "tags": keywords,
                "keywords": site_keywords,
            }
        )

        if isinstance(routes, dict):
            for route, relative_path in routes.items():
                if not isinstance(route, str) or not isinstance(relative_path, str):
                    continue
                html_path = (REPO_ROOT / root / relative_path).resolve()
                if not html_path.exists() or not html_path.is_file():
                    continue
                html = html_path.read_text(encoding="utf-8", errors="ignore")
                page_title = extract_title(html, f"{title} {route}")
                meta_description = extract_meta_content(html, "description")
                meta_keywords = extract_meta_content(html, "keywords")
                canonical_url = extract_meta_content(html, "og:url") or extract_meta_content(html, "twitter:url")
                headings = extract_headings(html)
                body = body_from_html(html)
                snippet = snippet_from_html(html, meta_description or description)
                page_description = meta_description or description
                parsed_meta_keywords = [part.strip() for part in meta_keywords.split(",") if part.strip()]
                page_keywords = [
                    item
                    for item in [domain, page_title, page_description, route, *headings, *keywords, *parsed_meta_keywords]
                    if item
                ]
                entries.append(
                    {
                        "type": "Page",
                        "domain": domain,
                        "url": canonical_url or f"https://{domain}{route}",
                        "canonical_url": canonical_url or f"https://{domain}{route}",
                        "title": page_title,
                        "description": page_description,
                        "snippet": snippet,
                        "headings": headings,
                        "body": body,
                        "tags": keywords,
                        "keywords": page_keywords,
                    }
                )

    for listing in load_agora_listings():
        name = str(listing.get("name", "")).strip()
        details = str(listing.get("details", "")).strip()
        if not name:
            continue
        listing_id = str(listing.get("id", "")).strip() or name.lower().replace(" ", "-")
        entries.append(
            {
                "type": "Listing",
                "domain": "agoramarket.com",
                "url": f"https://agoramarket.com/#listing-{listing_id}",
                "canonical_url": f"https://agoramarket.com/#listing-{listing_id}",
                "title": name,
                "description": details,
                "snippet": details,
                "headings": [name],
                "body": details,
                "tags": ["listing", "agora"],
                "keywords": ["agora market", name, details, str(listing.get("seller", "")).strip()],
            }
        )

    return {
        "version": 1,
        "generated_from": "registry.json",
        "entry_count": len(entries),
        "entries": entries,
    }


def main() -> int:
    index = build_index()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"Built search index: {OUTPUT_PATH.relative_to(REPO_ROOT)} ({index['entry_count']} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
