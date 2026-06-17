# AGENTS.md — WorldWeb Agent Guide

Read this file first.

Terminology note:
WorldWeb is the current name for the fake/local in-game internet layer. Some existing Hermes_OS code paths and directories may still use legacy/internal names such as `hermes_internet`. Do not introduce new user-facing uses of the old name.

WorldWeb is the static, bundled in-game internet content repository for HermesOS.

WorldWeb sites are authored like real web projects, built/exported as static HTML/CSS/JS, then consumed by HermesOS Browser as local bundled content. WorldWeb is not the real internet and must not require live servers, localhost sidecars, Docker services, or external network access.

## Core Rules

* Keep WorldWeb static and bundled.
* Do not add server dependencies.
* Do not add localhost, Docker, sidecar, bridge, or daemon requirements.
* Do not add real internet access or external fetching.
* Do not add secrets, API keys, tokens, remote auth, or deployment credentials.
* Do not modify HermesOS from this repo unless the task explicitly calls for sync/integration.
* Validate before reporting success.
* Do not stage, commit, push, pull, merge, rebase, reset, clean, or restore unless Kyle explicitly asks.

## Project Model

WorldWeb has two related layers:

```text
apps/
  Framework-authored source apps.
  Example: apps/agora-market, apps/pythia-search

sites/
  Static bundled output consumed by HermesOS Browser.
  Example: sites/agoramarket.com, sites/pythia.com

tools/
  Build, export, validation, search-index, and sync tooling.

registry.json
  WorldWeb domain/site registry.

worldweb.sites.json
  Framework-site pipeline registry.
```

The source of truth for framework-authored sites is usually under `apps/<site-id>/`.

The static runtime output lives under `sites/<domain>/`.

HermesOS consumes a synced/bundled copy of selected `sites/<domain>/` directories.

## Normal Domain Policy

WorldWeb may use normal-looking domains:

```text
agoramarket.com
pythia.com
charonwallet.com
athenatrust.org
oracleboard.net
aresmarket.com
```

Do not assume fake vs real internet based on suffix.

Fake vs real internet is determined by the active resolver/network context in HermesOS Browser.

WorldWeb domains resolve locally when registered and bundled. Unknown domains should remain external/disabled in HermesOS unless explicitly registered.

## Framework Site Pipeline

WorldWeb supports modern framework-authored sites.

Current preferred stack:

```text
Vite + Svelte
static export
bundled output
```

Other frameworks may be added later if they compile to static HTML/CSS/JS without server runtime requirements.

Use the generic pipeline instead of creating bespoke scripts per site.

Important files:

```text
worldweb.sites.json
tools/worldweb_site_pipeline.py
package.json
```

Expected commands may include:

```text
npm run site:build-all
npm run site:export-all
npm run site:validate
npm run site:check-js
python3 tools/worldweb_site_pipeline.py list
python3 tools/worldweb_site_pipeline.py build --site <site-id>
python3 tools/worldweb_site_pipeline.py export --site <site-id>
python3 tools/worldweb_site_pipeline.py sync --site <site-id>
```

If command names differ, inspect `package.json` and `tools/worldweb_site_pipeline.py`.

## Building Sites with Web Frameworks

WorldWeb sites may be authored with modern web frameworks as long as the final output is static, bundled, and compatible with HermesOS Browser.

Preferred current approach:

```text
Vite + Svelte
```

Other acceptable framework choices may include:

```text
Vite + React
Vite + Vue
Astro with static output
plain HTML/CSS/JavaScript
```

Framework choice should be driven by the site’s needs. Use the simplest tool that can produce the desired experience.

Use framework-authored sites for:

```text
marketplaces
search engines
wallet/payment dashboards
social/profile pages
interactive apps
settings/admin surfaces
rich UI-heavy pages
```

Use plain static HTML/CSS/JS for:

```text
simple landing pages
locked/teaser pages
documentation-style pages
small static notices
error pages
low-interaction content
```

Framework-authored sites must follow these rules:

* Source code lives under `apps/<site-id>/`.
* Static output lives under `sites/<domain>/`.
* The site must be registered in `worldweb.sites.json`.
* The domain/site must be registered in `registry.json` when it should exist on WorldWeb.
* The site must build through the generic WorldWeb pipeline.
* The exported site must not require a dev server.
* The exported site must not require SSR.
* The exported site must not require external APIs.
* The exported site must not load assets from external CDNs.
* The exported site must not depend on live network access.
* The exported site must work as bundled static content inside HermesOS Browser.

A framework site should be treated like a real web project during authoring, but like static game content at runtime.

Good pattern:

```text
apps/agora-market/
  source Svelte/Vite app

sites/agoramarket.com/
  generated static WorldWeb site
```

Bad pattern:

```text
HermesOS starts Vite dev server at runtime
HermesOS requires localhost to render a site
site loads scripts from a CDN
site fetches live external APIs
site requires Node/Bun/Deno during gameplay
```

Do not embed framework compiler/runtime requirements into HermesOS unless Kyle explicitly asks for an in-game builder/compiler feature later.

For now, the build pipeline belongs in the WorldWeb repo, not inside HermesOS runtime.

## Framework Build Expectations

Framework builds should be repeatable from repo scripts.

Expected commands should follow the generic pipeline where possible:

```bash
npm run site:build-all
npm run site:export-all
python3 tools/validate_world_web.py
```

For a single site, prefer the generic site pipeline:

```bash
python3 tools/worldweb_site_pipeline.py build --site <site-id>
python3 tools/worldweb_site_pipeline.py export --site <site-id>
python3 tools/worldweb_site_pipeline.py sync --site <site-id>
```

Compatibility aliases for important sites are allowed, such as:

```bash
npm run build:agora
npm run export:agora
npm run sync:agora
```

But do not create a new bespoke build system for every site.

## Static Export Compatibility

Generated sites must be static and bundled.

A built site should not require:

```text
npm dev server
Vite dev server
localhost
Docker
external CDN
external API
remote fonts
remote scripts
live backend
```

Framework-built pages should be exportable into `sites/<domain>/`.

Because HermesOS Browser may load WorldWeb pages through local document loading rather than a real web server, framework output must be compatible with local bundled loading.

When needed, the export pipeline may inline local JavaScript and CSS into the generated HTML.

Inlining rules:

* Inline local generated assets when needed for HermesOS compatibility.
* Preserve module script behavior where required.
* Do not inline remote assets.
* Do not fetch external URLs.
* Do not hardcode content-hashed filenames manually.
* Keep inlining automated through the pipeline.

If a framework site renders blank in HermesOS Browser, first check:

```text
generated asset paths
script and stylesheet references
whether CSS/JS were inlined correctly
whether the site was synced into HermesOS
whether HermesOS registry includes the domain
whether the browser is showing Real Internet disabled
```

Do not fix blank framework pages by adding real network access or local servers.

## Shared Data for Framework Sites

Prefer shared structured data when multiple WorldWeb sites need the same content.

Examples:

```text
Agora Market listings
Pythia Search index input
merchant metadata
site descriptions
search keywords
```

Good:

```text
shared JSON or deterministic module consumed by both the source app and build tools
```

Avoid:

```text
scraping generated HTML as the primary data source
duplicating the same listing data in multiple apps
hardcoding search-only copies of marketplace data
```

If data starts in JavaScript for convenience, that is acceptable for early build mode, but prefer moving stable cross-site data to JSON once multiple sites depend on it.

## UI Quality Expectations

Framework-authored WorldWeb sites should look and feel like real modern websites.

Aim for:

* clear layout
* responsive sizing inside HermesOS Browser windows
* polished typography
* good spacing
* reusable components
* clear interaction states
* empty states
* loading/error states where relevant
* keyboard-friendly controls where practical

Do not accept “it technically works” if the site looks like raw test markup, unless the task is explicitly a rough prototype.

WorldWeb should feel like a real internet inside the game.

## Static Export Requirements

Generated sites must be static and bundled.

A built site should not require:

```text
npm dev server
Vite dev server
localhost
Docker
external CDN
external API
remote fonts
remote scripts
live backend
```

Framework-built pages should be exportable into `sites/<domain>/`.

Because HermesOS Browser may load pages through local `load_html()` style flows, framework pages should be self-contained or otherwise compatible with HermesOS local loading.

When needed, the pipeline may inline local CSS/JS assets into exported HTML. Do not fetch or inline remote assets.

## Search / Pythia

Pythia Search is the WorldWeb search engine.

Scope:

```text
pythia.com
Search indexed WorldWeb sites, pages, and listings.
```

Pythia is only a search engine.

Do not add unless explicitly requested:

```text
rumor feeds
prophecy/oracle mechanics
AI answer cards
chatbot behavior
sponsored results
hidden lore systems
crypto mechanics
Ares/StyxNet expansion
social features
```

Search index generation should remain static/build-time.

Relevant tooling may include:

```text
tools/build_search_index.py
sites/pythia.com/data/search-index.json
```

WorldWeb SEO/search metadata means local searchable metadata such as:

```text
title
description
keywords
tags
canonical URL
domain
headings
body snippets
structured listing data
```

Prefer reusable structured data over scraping generated HTML when practical.

## Site Naming

Keep `WorldWeb` as the platform/internet layer.

Use distinct names for sites and services. Avoid naming every new product “Hermes.”

Current naming direction:

```text
Agora Market
  Clear-web marketplace.

Pythia Search
  WorldWeb search engine.

Charon Wallet
  Wallet/payment surface, future.

Athena Trust
  Reputation/trust surface, future.

Oracle Board
  Board/forum/info surface, future.

Ares Market
  Locked/teaser only unless explicitly assigned.

StyxNet
  Hidden network layer, future only.
```

Do not implement crypto, Ares Market, StyxNet, or dark-web economy unless explicitly assigned.

## Validation

Always validate before reporting success.

Baseline validation:

```bash
python3 tools/validate_world_web.py
```

For framework/pipeline work, also run relevant commands such as:

```bash
npm run site:build-all
npm run site:export-all
npm run site:check-js
```

For search/index work, verify:

```text
search index exists
entry count is reasonable
required domains are indexed
expected result types exist
queries return expected results
nonsense query returns empty state
```

For sync work, verify the target HermesOS bundle only if the task explicitly includes HermesOS sync.

## Git / Change Discipline

Default mode is Build Mode.

In Build Mode:

```text
dirty tree is allowed
do not stage
do not commit
do not push
do not call hermes-git unless Kyle asks for checkpoint/commit/push
report changed files and validation
keep moving
```

Checkpoint only when Kyle explicitly asks or a larger playable milestone is ready.

When checkpointing:

```text
use hermes-git
stage exact paths only
never use git add .
never use git add -A
do not commit generated/noise files unless intentionally part of the checkpoint
do not push without explicit approval or a push-readiness gate
```

Generated/local noise should usually remain uncommitted unless intentionally tracked.

Examples:

```text
tools/pycache/
node_modules/
temporary build/cache files
```

## Working with HermesOS

WorldWeb is the source of truth for WorldWeb sites.

HermesOS is the bundled runtime consumer.

Only touch HermesOS when the task explicitly requires:

```text
syncing a built site into HermesOS content
updating HermesOS registry copy
testing Browser resolver integration
fixing HermesOS Browser behavior
```

Do not modify HermesOS incidentally from WorldWeb tasks.

When syncing to HermesOS, keep it bounded:

```text
copy registered site output
update only required registry/content files
do not touch unrelated HermesOS files
do not clean unrelated dirty files
```

## Agent Workflow

When working in this repo:

1. Read this file.
2. Read the user’s current task.
3. Inspect only task-relevant files.
4. Use the existing pipeline before inventing new tooling.
5. Make the smallest useful change.
6. Validate.
7. Report clearly.

Report format:

```text
Files added:
Files modified:
Files deleted:
Commands/checks run:
Validation result:
Known limitations:
Git status:
Recommended next step:
```

## Final Rule

WorldWeb should feel like a real web codebase that produces a fictional, local, bundled internet for HermesOS.

Build real sites in code.

Export static sites for the game.

Keep the runtime local, safe, deterministic, and bundled.
