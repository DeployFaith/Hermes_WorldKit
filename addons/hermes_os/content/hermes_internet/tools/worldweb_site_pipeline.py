#!/usr/bin/env python3
"""Generalized build/export/sync pipeline for framework-authored WorldWeb sites."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = REPO_ROOT / "worldweb.sites.json"
HERMES_OS_ROOT = (REPO_ROOT.parent / "HermesOS").resolve()


class PipelineError(Exception):
    pass


@dataclass
class SiteConfig:
    id: str
    enabled: bool
    domain: str
    app_dir: Path
    site_root: Path
    build_command: list[str] | None
    export_command: list[str] | None
    sync_source: Path | None
    sync_destination: Path | None


def load_config(config_path: Path) -> list[SiteConfig]:
    if not config_path.exists():
        raise PipelineError(f"Missing config: {config_path}")

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PipelineError(f"Invalid JSON in {config_path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise PipelineError("Config root must be a JSON object")

    sites_raw = raw.get("sites")
    if not isinstance(sites_raw, list):
        raise PipelineError("Config 'sites' must be an array")

    sites: list[SiteConfig] = []
    seen_ids: set[str] = set()

    for index, entry in enumerate(sites_raw):
        if not isinstance(entry, dict):
            raise PipelineError(f"sites[{index}] must be an object")

        site_id = str(entry.get("id", "")).strip()
        if not site_id:
            raise PipelineError(f"sites[{index}] missing id")
        if site_id in seen_ids:
            raise PipelineError(f"Duplicate site id: {site_id}")
        seen_ids.add(site_id)

        enabled = bool(entry.get("enabled", True))
        domain = str(entry.get("domain", "")).strip()
        if not domain:
            raise PipelineError(f"site '{site_id}' missing domain")

        app_dir = resolve_repo_path(site_id, "app_dir", entry.get("app_dir"))
        site_root = resolve_repo_path(site_id, "site_root", entry.get("site_root"))

        build_command = parse_command(entry.get("build"), site_id, "build")
        export_command = parse_command(entry.get("export"), site_id, "export")

        sync_cfg = entry.get("sync")
        sync_source: Path | None = None
        sync_destination: Path | None = None
        if sync_cfg is not None:
            if not isinstance(sync_cfg, dict):
                raise PipelineError(f"site '{site_id}' sync must be an object")
            sync_source = resolve_repo_path(site_id, "sync.source", sync_cfg.get("source"))
            sync_destination = resolve_sync_destination(site_id, sync_cfg.get("destination"))

        sites.append(
            SiteConfig(
                id=site_id,
                enabled=enabled,
                domain=domain,
                app_dir=app_dir,
                site_root=site_root,
                build_command=build_command,
                export_command=export_command,
                sync_source=sync_source,
                sync_destination=sync_destination,
            )
        )

    return sites


def resolve_repo_path(site_id: str, field: str, value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise PipelineError(f"site '{site_id}' missing {field}")
    candidate = (REPO_ROOT / value).resolve()
    if not is_within(REPO_ROOT.resolve(), candidate):
        raise PipelineError(f"site '{site_id}' {field} escapes repo root: {value}")
    return candidate


def resolve_sync_destination(site_id: str, value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise PipelineError(f"site '{site_id}' missing sync.destination")
    candidate = (REPO_ROOT / value).resolve()
    if not is_within(HERMES_OS_ROOT, candidate):
        raise PipelineError(
            f"site '{site_id}' sync.destination must stay within HermesOS repo ({HERMES_OS_ROOT}): {value}"
        )
    return candidate


def parse_command(container: Any, site_id: str, phase: str) -> list[str] | None:
    if container is None:
        return None
    if not isinstance(container, dict):
        raise PipelineError(f"site '{site_id}' {phase} must be an object")

    command = container.get("command")
    if command is None:
        return None
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x.strip() for x in command):
        raise PipelineError(f"site '{site_id}' {phase}.command must be a non-empty string array")
    return [part.strip() for part in command]


def is_within(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def get_site(sites: list[SiteConfig], site_id: str) -> SiteConfig:
    for site in sites:
        if site.id == site_id:
            return site
    raise PipelineError(f"Unknown site id: {site_id}")


def run_command(command: list[str], cwd: Path, label: str) -> None:
    print(f"[{label}] Running: {' '.join(command)}")
    completed = subprocess.run(command, cwd=cwd)
    if completed.returncode != 0:
        raise PipelineError(f"{label} failed with exit code {completed.returncode}")


def build_site(site: SiteConfig) -> None:
    if not site.build_command:
        raise PipelineError(f"site '{site.id}' has no build command configured")
    run_command(site.build_command, REPO_ROOT, f"build:{site.id}")


def export_site(site: SiteConfig) -> None:
    if site.export_command:
        run_command(site.export_command, REPO_ROOT, f"export:{site.id}")
        report = inline_local_assets(site)
        embedded_index = embed_pythia_index(site)
        print(
            f"[export:{site.id}] Inlined assets: "
            f"html_files={report['html_files']} "
            f"css_inlined={report['css_inlined']} "
            f"scripts_inlined={report['scripts_inlined']} "
            f"external_or_blocked={report['external_or_blocked']} "
            f"missing_or_skipped={report['missing_or_skipped']} "
            f"embedded_index={embedded_index}"
        )
        return
    raise PipelineError(f"site '{site.id}' has no export command configured")


def inline_local_assets(site: SiteConfig) -> dict[str, int]:
    site_root = site.site_root
    if not site_root.exists() or not site_root.is_dir():
        raise PipelineError(f"site '{site.id}' site_root missing after export: {site_root}")

    html_paths = sorted(site_root.rglob("*.html"))
    totals = {
        "html_files": 0,
        "css_inlined": 0,
        "scripts_inlined": 0,
        "external_or_blocked": 0,
        "missing_or_skipped": 0,
    }

    for html_path in html_paths:
        original = html_path.read_text(encoding="utf-8")
        transformed, stats = inline_assets_in_html(original, html_path, site_root)
        if transformed != original:
            html_path.write_text(transformed, encoding="utf-8")
        totals["html_files"] += 1
        for key, value in stats.items():
            totals[key] += value

    return totals


def inline_assets_in_html(html: str, html_path: Path, site_root: Path) -> tuple[str, dict[str, int]]:
    stats = {
        "css_inlined": 0,
        "scripts_inlined": 0,
        "external_or_blocked": 0,
        "missing_or_skipped": 0,
    }

    def replace_stylesheet(match: re.Match[str]) -> str:
        tag = match.group(0)
        href = extract_attr(tag, "href")
        if not href:
            stats["missing_or_skipped"] += 1
            return tag
        if is_blocked_external_url(href):
            stats["external_or_blocked"] += 1
            return tag

        asset_path = resolve_local_asset_path(href, html_path, site_root)
        if asset_path is None:
            stats["missing_or_skipped"] += 1
            return tag

        css_content = asset_path.read_text(encoding="utf-8")
        media = extract_attr(tag, "media")
        media_attr = f' media="{media}"' if media else ""
        rel_path = asset_path.relative_to(site_root)
        stats["css_inlined"] += 1
        return f"<style data-worldweb-inlined-from=\"{rel_path.as_posix()}\"{media_attr}>\n{css_content}\n</style>"

    html = re.sub(
        r"<link\b[^>]*\brel=[\"'][^\"']*stylesheet[^\"']*[\"'][^>]*>",
        replace_stylesheet,
        html,
        flags=re.IGNORECASE,
    )

    def replace_script(match: re.Match[str]) -> str:
        tag = match.group(0)
        src = extract_attr(tag, "src")
        if not src:
            stats["missing_or_skipped"] += 1
            return tag
        if is_blocked_external_url(src):
            stats["external_or_blocked"] += 1
            return tag

        asset_path = resolve_local_asset_path(src, html_path, site_root)
        if asset_path is None:
            stats["missing_or_skipped"] += 1
            return tag

        script_content = asset_path.read_text(encoding="utf-8")
        open_tag_match = re.match(r"<script\b([^>]*)>", tag, flags=re.IGNORECASE | re.DOTALL)
        if open_tag_match is None:
            stats["missing_or_skipped"] += 1
            return tag
        attrs = open_tag_match.group(1)
        attrs = re.sub(r"\s+src\s*=\s*([\"']).*?\1", "", attrs, flags=re.IGNORECASE | re.DOTALL)
        attrs = re.sub(r"\s+crossorigin(?:\s*=\s*([\"']).*?\1)?", "", attrs, flags=re.IGNORECASE | re.DOTALL)
        attrs = re.sub(r"\s+", " ", attrs).strip()
        attrs_prefix = f" {attrs}" if attrs else ""
        rel_path = asset_path.relative_to(site_root)
        stats["scripts_inlined"] += 1
        return (
            f"<script{attrs_prefix} data-worldweb-inlined-from=\"{rel_path.as_posix()}\">\n"
            f"{script_content}\n"
            "</script>"
        )

    html = re.sub(
        r"<script\b[^>]*\bsrc=[\"'][^\"']+[\"'][^>]*>\s*</script>",
        replace_script,
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    return html, stats


def extract_attr(tag: str, attr_name: str) -> str | None:
    match = re.search(
        rf"\b{re.escape(attr_name)}\s*=\s*([\"'])(.*?)\1",
        tag,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    return match.group(2).strip()


def is_blocked_external_url(url: str) -> bool:
    lower = url.strip().lower()
    return (
        lower.startswith("http://")
        or lower.startswith("https://")
        or lower.startswith("//")
        or lower.startswith("data:")
        or lower.startswith("javascript:")
    )


def resolve_local_asset_path(asset_ref: str, html_path: Path, site_root: Path) -> Path | None:
    trimmed = asset_ref.strip()
    if not trimmed:
        return None
    path_only = trimmed.split("#", 1)[0].split("?", 1)[0]
    if not path_only:
        return None
    if path_only.startswith("/"):
        candidate = (site_root / path_only.lstrip("/")).resolve()
    else:
        candidate = (html_path.parent / path_only).resolve()
    if not is_within(site_root.resolve(), candidate):
        return None
    if not candidate.exists() or not candidate.is_file():
        return None
    return candidate


def embed_pythia_index(site: SiteConfig) -> int:
    if site.id != "pythia-search":
        return 0

    index_path = site.site_root / "data" / "search-index.json"
    if not index_path.exists() or not index_path.is_file():
        raise PipelineError(f"site '{site.id}' missing search index for embed: {index_path}")

    token = "__PYTHIA_SEARCH_INDEX_JSON__"
    payload = index_path.read_text(encoding="utf-8").strip()
    updated_files = 0

    for html_path in sorted(site.site_root.rglob("*.html")):
        original = html_path.read_text(encoding="utf-8")
        if token not in original:
            continue
        html_path.write_text(original.replace(token, payload), encoding="utf-8")
        updated_files += 1

    if updated_files == 0:
        raise PipelineError(f"site '{site.id}' did not contain embed token '{token}' in exported HTML")

    return updated_files


def sync_site(site: SiteConfig) -> None:
    if site.sync_source is None or site.sync_destination is None:
        raise PipelineError(f"site '{site.id}' has no sync config")

    source = site.sync_source
    destination = site.sync_destination

    if not source.exists() or not source.is_dir():
        raise PipelineError(f"sync source missing for '{site.id}': {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, dirs_exist_ok=True)
    print(f"[sync:{site.id}] Copied {source.relative_to(REPO_ROOT)} -> {destination}")


def list_sites(sites: list[SiteConfig]) -> int:
    print("WORLDWEB_SITES")
    for site in sites:
        state = "enabled" if site.enabled else "disabled"
        print(f"- {site.id} ({site.domain}) [{state}]")
    return 0


def run_for_one(sites: list[SiteConfig], site_id: str, action: str) -> int:
    site = get_site(sites, site_id)
    if action == "build":
        build_site(site)
    elif action == "export":
        export_site(site)
    elif action == "sync":
        sync_site(site)
    else:
        raise PipelineError(f"Unsupported action: {action}")

    print(f"RESULT: {action} ok for {site.id}")
    return 0


def run_for_all(sites: list[SiteConfig], action: str) -> int:
    enabled_sites = [site for site in sites if site.enabled]
    if not enabled_sites:
        print("No enabled sites")
        return 0

    for site in enabled_sites:
        print(f"== {action} {site.id} ==")
        if action == "build":
            build_site(site)
        elif action == "export":
            export_site(site)
        elif action == "sync":
            sync_site(site)
        else:
            raise PipelineError(f"Unsupported action: {action}")

    print(f"RESULT: {action}-all ok ({len(enabled_sites)} site(s))")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WorldWeb site pipeline")
    parser.add_argument("action", choices=["list", "build", "export", "sync", "build-all", "export-all", "sync-all"])
    parser.add_argument("--site", help="Site id for one-site actions")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to worldweb site config JSON")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    config_path = Path(args.config).resolve()
    try:
        sites = load_config(config_path)

        if args.action == "list":
            return list_sites(sites)

        if args.action in {"build", "export", "sync"}:
            if not args.site:
                raise PipelineError(f"--site is required for action '{args.action}'")
            return run_for_one(sites, args.site, args.action)

        if args.action == "build-all":
            return run_for_all(sites, "build")
        if args.action == "export-all":
            return run_for_all(sites, "export")
        if args.action == "sync-all":
            return run_for_all(sites, "sync")

        raise PipelineError(f"Unhandled action: {args.action}")
    except PipelineError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
