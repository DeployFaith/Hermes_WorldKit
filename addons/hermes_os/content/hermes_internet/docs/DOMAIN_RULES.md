# Domain rules

Current allowed TLD:
- `.hermes`

Rules:
- Domains must be lowercase.
- Matching is exact by host.
- `home.hermes.evil` must not be treated as `home.hermes`.
- Route lookup is based on the exact registered domain in `registry.json`.
