#!/usr/bin/env python3
"""Validate world-web static content structure and safety rules."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registry.json"
SYSTEM_NOT_FOUND_PATH = REPO_ROOT / "system" / "not_found.html"

PLACEHOLDER_DOMAINS = ["news.grid", "atlas.node", "vault.corp"]
BLOCKED_ROUTE_SUBSTRINGS = ["localhost", "127.0.0.1", "http://", "https://"]
BLOCKED_SCRIPT_SRC_SUBSTRINGS = ["http://", "https://", "localhost", "127.0.0.1"]
ALLOWED_DOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.(?:hermes|com|net|org)$")
CONTENT_SCAN_GLOBS = ["*.json", "*.html", "*.css", "*.js"]
SCRIPT_SRC_RE = re.compile(r"<script\b[^>]*\bsrc\s*=\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
REQUIRED_HOME_HERMES_ROUTES = ["/interactive", "/games", "/games/snake"]


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.passes: list[str] = []

    def ok(self, message: str) -> None:
        self.passes.append(message)

    def fail(self, message: str) -> None:
        self.errors.append(message)


def load_json(path: Path, v: Validation, label: str) -> dict | None:
    if not path.exists():
        v.fail(f"{label} missing: {path.relative_to(REPO_ROOT)}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        v.fail(f"{label} invalid JSON: {path.relative_to(REPO_ROOT)} ({exc})")
        return None
    if not isinstance(data, dict):
        v.fail(f"{label} must be a JSON object: {path.relative_to(REPO_ROOT)}")
        return None
    v.ok(f"{label} parses: {path.relative_to(REPO_ROOT)}")
    return data


def is_within(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def domain_allowed(domain: str) -> bool:
    return bool(ALLOWED_DOMAIN_RE.fullmatch(domain))


def scan_for_placeholders(v: Validation) -> None:
    scan_roots = [
        REPO_ROOT / "registry.json",
        REPO_ROOT / "sites",
        REPO_ROOT / "system",
    ]
    text_files: set[Path] = set()

    for root in scan_roots:
        if root.is_file():
            text_files.add(root)
            continue
        if not root.exists():
            continue
        for glob in CONTENT_SCAN_GLOBS:
            for path in root.rglob(glob):
                if ".git" in path.parts:
                    continue
                if path.is_file():
                    text_files.add(path)

    for path in sorted(text_files):
        lower = path.read_text(encoding="utf-8", errors="ignore").lower()
        for placeholder in PLACEHOLDER_DOMAINS:
            if placeholder in lower:
                v.fail(f"Placeholder domain '{placeholder}' found in {path.relative_to(REPO_ROOT)}")


def validate_html_script_sources(
    v: Validation,
    *,
    domain: str,
    site_root: Path,
    route_path: str,
    route_target: str,
    html_path: Path,
) -> None:
    if html_path.suffix.lower() not in {".html", ".htm"}:
        return

    raw_html = html_path.read_text(encoding="utf-8", errors="ignore")
    html_dir = html_path.parent.resolve()

    for src in SCRIPT_SRC_RE.findall(raw_html):
        script_src = src.strip()
        if not script_src:
            v.fail(f"{domain} script src is empty in {route_target}")
            continue

        src_lower = script_src.lower()
        for bad in BLOCKED_SCRIPT_SRC_SUBSTRINGS:
            if bad in src_lower:
                v.fail(f"{domain} route {route_path} script src has forbidden token '{bad}': {script_src}")

        if src_lower.startswith("//"):
            v.fail(f"{domain} route {route_path} script src must not be protocol-relative: {script_src}")
            continue

        if re.match(r"^[a-z][a-z0-9+.-]*:", src_lower):
            v.fail(f"{domain} route {route_path} script src must be local relative path: {script_src}")
            continue

        script_src_path = script_src.split("?", 1)[0].split("#", 1)[0]
        if not script_src_path:
            v.fail(f"{domain} route {route_path} script src path is empty: {script_src}")
            continue

        if Path(script_src_path).is_absolute():
            v.fail(f"{domain} route {route_path} script src must be relative (not absolute): {script_src}")
            continue

        resolved_script_path = (html_dir / script_src_path).resolve()
        if not is_within(site_root.resolve(), resolved_script_path):
            v.fail(f"{domain} route {route_path} script src escapes site root: {script_src}")
            continue

        if not resolved_script_path.exists() or not resolved_script_path.is_file():
            v.fail(f"{domain} route {route_path} script src missing: {script_src}")
            continue

        v.ok(f"Script src valid: {domain} {route_path} -> {script_src}")


def validate() -> int:
    v = Validation()

    registry = load_json(REGISTRY_PATH, v, "registry.json")
    if registry is None:
        print_report(v)
        return 1

    version = registry.get("version")
    if version is None:
        v.fail("registry.json missing 'version'")
    else:
        v.ok("registry.json has version")

    sites_raw = registry.get("sites")
    if not isinstance(sites_raw, list):
        v.fail("registry.json 'sites' must be an array")
        sites_raw = []

    seen_domains: set[str] = set()
    registered_domains: set[str] = set()

    for idx, entry in enumerate(sites_raw):
        site_label = f"sites[{idx}]"
        if not isinstance(entry, dict):
            v.fail(f"{site_label} must be an object")
            continue

        domain = str(entry.get("domain", "")).strip()
        if not domain:
            v.fail(f"{site_label} missing domain")
            continue

        registered_domains.add(domain)

        if domain != domain.lower():
            v.fail(f"{site_label} domain must be lowercase: {domain}")

        if domain in seen_domains:
            v.fail(f"Duplicate domain in registry: {domain}")
        else:
            seen_domains.add(domain)
            v.ok(f"Unique domain: {domain}")

        if not domain_allowed(domain):
            v.fail(f"Domain not allowed (must be valid .hermes/.com/.net/.org): {domain}")
        else:
            v.ok(f"Domain allowed: {domain}")

        root_value = str(entry.get("root", "")).strip()
        if not root_value:
            v.fail(f"{site_label} missing root")
            continue
        if root_value.startswith("res://"):
            v.fail(f"{site_label} root must be repo-relative, not res:// ({root_value})")

        site_root = (REPO_ROOT / root_value).resolve()
        if not site_root.exists() or not site_root.is_dir():
            v.fail(f"Site root missing for {domain}: {root_value}")
            continue
        if not is_within(REPO_ROOT.resolve(), site_root):
            v.fail(f"Site root escapes repo for {domain}: {root_value}")
            continue
        v.ok(f"Site root exists: {root_value}")

        site_json_path = site_root / "site.json"
        site_json = load_json(site_json_path, v, f"site.json for {domain}")
        if site_json is None:
            continue

        site_domain = str(site_json.get("domain", "")).strip()
        if site_domain != domain:
            v.fail(f"site.json domain mismatch for {domain}: found '{site_domain}'")
        else:
            v.ok(f"site.json domain matches for {domain}")

        routes = entry.get("routes")
        if not isinstance(routes, dict):
            v.fail(f"{site_label} routes must be an object")
            continue

        for route_path, route_target in routes.items():
            if not isinstance(route_path, str):
                v.fail(f"{domain} has non-string route key: {route_path!r}")
                continue
            if not route_path.startswith("/"):
                v.fail(f"{domain} route must start with '/': {route_path}")

            if not isinstance(route_target, str) or not route_target.strip():
                v.fail(f"{domain} route target must be a non-empty string for {route_path}")
                continue

            target_lower = route_target.lower()
            for bad in BLOCKED_ROUTE_SUBSTRINGS:
                if bad in target_lower:
                    v.fail(f"{domain} route target for {route_path} contains forbidden token '{bad}': {route_target}")

            target_path = (site_root / route_target).resolve()
            if not is_within(site_root.resolve(), target_path):
                v.fail(f"{domain} route target escapes site root: {route_path} -> {route_target}")
                continue

            if not target_path.exists() or not target_path.is_file():
                v.fail(f"{domain} route target missing: {route_path} -> {route_target}")
            else:
                v.ok(f"Route exists: {domain} {route_path} -> {route_target}")
                validate_html_script_sources(
                    v,
                    domain=domain,
                    site_root=site_root,
                    route_path=route_path,
                    route_target=route_target,
                    html_path=target_path,
                )

        if domain == "home.hermes":
            for required_route in REQUIRED_HOME_HERMES_ROUTES:
                if required_route not in routes:
                    v.fail(f"home.hermes missing required route: {required_route}")
                else:
                    v.ok(f"home.hermes required route present: {required_route}")

    default_domain = str(registry.get("default_domain", "")).strip()
    if not default_domain:
        v.fail("registry.json missing default_domain")
    elif default_domain not in registered_domains:
        v.fail(f"default_domain not registered in sites: {default_domain}")
    else:
        v.ok(f"default_domain is registered: {default_domain}")

    if not SYSTEM_NOT_FOUND_PATH.exists() or not SYSTEM_NOT_FOUND_PATH.is_file():
        v.fail("system/not_found.html is missing")
    else:
        v.ok("system/not_found.html exists")

    scan_for_placeholders(v)

    print_report(v)
    return 1 if v.errors else 0


def print_report(v: Validation) -> None:
    print("WORLD_WEB_VALIDATION")
    for message in v.passes:
        print(f"PASS: {message}")
    for message in v.errors:
        print(f"FAIL: {message}")
    if v.errors:
        print(f"RESULT: FAIL ({len(v.errors)} error(s))")
    else:
        print("RESULT: PASS")


if __name__ == "__main__":
    raise SystemExit(validate())
