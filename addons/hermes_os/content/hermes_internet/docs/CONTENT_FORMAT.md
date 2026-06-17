# Content format

## registry.json

Top-level fields:
- `version` (integer)
- `product` (string)
- `default_domain` (string)
- `sites` (array)

Each `sites[]` item:
- `domain` (string, lowercase, `.hermes`)
- `title` (string)
- `description` (string)
- `root` (string, repo-relative path like `sites/home.hermes`)
- `entry` (string route, usually `/`)
- `routes` (object mapping route path -> file path under site root)
- `agent_visible` (boolean)

Example route mapping:

```json
"routes": {
  "/": "pages/index.html",
  "/interactive": "pages/interactive.html",
  "/games": "pages/games.html",
  "/games/snake": "pages/games_snake.html"
}
```

## site.json

Location:
- `sites/<domain>/site.json`

Fields:
- `domain`
- `title`
- `description`
- `entry`
- `routes`
- `agent_visible`

Notes:
- `site.json` `domain` must match the `registry.json` entry domain.
- Route keys must start with `/`.
- Route targets must stay inside that site root.
- Route targets must be static files (no HTTP/localhost targets).

## local JavaScript assets

Recommended structure:
- `sites/<domain>/pages/*.html`
- `sites/<domain>/styles/*.css`
- `sites/<domain>/scripts/*.js`

Script rules enforced by validator:
- Script `src` must be local relative paths.
- Script `src` must not include `http://` or `https://`.
- Script `src` must not include `localhost` or `127.0.0.1`.
- Script `src` must resolve within the same site root.
- Referenced script files must exist.
