# world-web

WorldWeb is the static content repository for the in-game WorldWeb layer.

WorldWeb is the bundled/local WorldWeb content for Hermes_OS. It is static content loaded from files and does not require Docker, localhost, sidecars, bridges, or servers.

Terminology note:
WorldWeb is the current name for the fake/local in-game internet layer. Some existing Hermes_OS code paths and directories may still use legacy/internal names such as `hermes_internet`. Do not introduce new user-facing uses of the old name.

Current official site:
- `home.hermes`

Structure:
- `registry.json` maps domains and routes.
- `sites/<domain>/` stores site content.
- `sites/<domain>/pages/` stores route HTML files.
- `sites/<domain>/styles/` stores local CSS assets.
- `sites/<domain>/scripts/` stores local JavaScript assets.
- `system/not_found.html` is the fallback template.

Current demo routes in `home.hermes`:
- `/`
- `/interactive`
- `/games`
- `/games/snake`

JavaScript policy:
- Local relative script paths only.
- No `http://` or `https://` scripts.
- No `localhost`/`127.0.0.1` script paths.
- No script paths escaping the site root.

Validate:

```bash
python3 tools/validate_world_web.py
```
