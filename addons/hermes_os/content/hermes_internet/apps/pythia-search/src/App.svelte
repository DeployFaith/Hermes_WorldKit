<script>
  const TYPE_WEIGHT = { Site: 0, Page: 1, Listing: 2 };
  const FIELD_WEIGHTS = {
    title: 14,
    domain: 12,
    url: 10,
    description: 8,
    snippet: 5,
    tags: 7,
    keywords: 6,
    headings: 6,
    body: 4
  };
  let query = '';
  let activeQuery = '';
  let allEntries = [];
  let loading = true;

  function tokenize(text) {
    return String(text || '')
      .toLowerCase()
      .split(/[^a-z0-9]+/)
      .filter(Boolean);
  }

  function normalize(text) {
    return String(text || '').toLowerCase().replace(/\s+/g, ' ').trim();
  }

  function countTokenMatches(fieldText, terms) {
    const tokens = tokenize(fieldText);
    if (!tokens.length) return 0;
    const tokenSet = new Set(tokens);
    let matches = 0;
    for (const term of terms) {
      if (tokenSet.has(term)) {
        matches += 1;
      }
    }
    return matches;
  }

  function scoreEntry(entry, q) {
    const terms = tokenize(q);
    if (!terms.length) {
      return 0;
    }
    const phrase = normalize(q);
    const fields = {
      title: entry.title,
      domain: entry.domain,
      url: entry.url,
      description: entry.description,
      snippet: entry.snippet,
      tags: (entry.tags || []).join(' '),
      keywords: (entry.keywords || []).join(' '),
      headings: (entry.headings || []).join(' '),
      body: entry.body || entry.snippet || ''
    };
    let score = 0;

    for (const [fieldName, weight] of Object.entries(FIELD_WEIGHTS)) {
      const fieldText = normalize(fields[fieldName]);
      if (!fieldText) continue;

      if (fieldText.includes(phrase)) {
        score += weight * 3;
      }

      const tokenMatches = countTokenMatches(fieldText, terms);
      if (tokenMatches > 0) {
        score += tokenMatches * weight;
      }
    }

    return score;
  }

  $: results = (() => {
    const trimmed = activeQuery.trim();
    if (!trimmed) return [];
    return allEntries
      .map((entry) => ({ entry, score: scoreEntry(entry, trimmed) }))
      .filter((pair) => pair.score > 0)
      .sort((a, b) => {
        if (b.score !== a.score) return b.score - a.score;
        const typeDelta = (TYPE_WEIGHT[a.entry.type] ?? 99) - (TYPE_WEIGHT[b.entry.type] ?? 99);
        if (typeDelta !== 0) return typeDelta;
        return a.entry.title.localeCompare(b.entry.title);
      })
      .map((pair) => pair.entry);
  })();

  $: if (typeof window !== 'undefined') {
    window.__PYTHIA_SEARCH_READY = !loading;
    window.__PYTHIA_LAST_QUERY = activeQuery;
    window.__PYTHIA_RESULT_COUNT = results.length;
  }

  function submitSearch() {
    const next = query.trim();
    const params = new URLSearchParams(window.location.search);
    if (next) params.set('q', next);
    else params.delete('q');
    const nextUrl = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ''}`;
    window.history.replaceState({}, '', nextUrl);
    activeQuery = next;
  }

  function formatDisplayUrl(result) {
    const fallback = result?.domain || '';
    if (!result?.url) {
      return fallback;
    }

    try {
      const parsed = new URL(result.url);
      const path = `${parsed.pathname || ''}${parsed.search || ''}${parsed.hash || ''}`;
      return `${parsed.host}${path}`;
    } catch {
      return fallback || result.url;
    }
  }

  async function loadIndex() {
    const response = await fetch('../data/search-index.json');
    if (!response.ok) {
      allEntries = [];
      loading = false;
      return;
    }
    const payload = await response.json();
    allEntries = Array.isArray(payload.entries) ? payload.entries : [];
    loading = false;

    const params = new URLSearchParams(window.location.search);
    query = params.get('q') || '';
    activeQuery = query.trim();
  }

  window.addEventListener('popstate', () => {
    const params = new URLSearchParams(window.location.search);
    query = params.get('q') || '';
    activeQuery = query.trim();
  });

  loadIndex();
</script>

<main>
  {#if !activeQuery}
    <section class="hero">
      <a class="brand" href="./">Pythia Search</a>
      <h1>Search WorldWeb</h1>
      <form class="hero-form" on:submit|preventDefault={submitSearch}>
        <label class="sr-only" for="search-input">Search WorldWeb</label>
        <input id="search-input" type="search" bind:value={query} placeholder="Search WorldWeb" autocomplete="off" />
        <button type="submit">Search</button>
      </form>
      <p>Search indexed WorldWeb sites, pages, and marketplace listings.</p>
    </section>
  {:else}
    <header class="results-header">
      <a class="brand" href="./">Pythia Search</a>
      <form class="results-form" on:submit|preventDefault={submitSearch}>
        <label class="sr-only" for="results-search-input">Search WorldWeb</label>
        <input id="results-search-input" type="search" bind:value={query} placeholder="Search WorldWeb" autocomplete="off" />
        <button type="submit">Search</button>
      </form>
    </header>

    <section class="results-head">
      <h1>Results</h1>
      <p>"{activeQuery}" · {results.length} result{results.length === 1 ? '' : 's'}</p>
    </section>

    {#if loading}
      <p class="empty">Loading index...</p>
    {:else if !results.length}
      <p class="empty">No results found for "{activeQuery}".</p>
    {:else}
      <section class="results-list" aria-live="polite">
        {#each results as result}
          <article>
            <div class="top-row">
              <span class="type">{result.type}</span>
              <a class="url" href={result.url}>{formatDisplayUrl(result)}</a>
            </div>
            <h2><a href={result.url}>{result.title}</a></h2>
            <p>{result.snippet || result.description}</p>
          </article>
        {/each}
      </section>
    {/if}
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    background: #0a101d;
    color: #e8ecf8;
    font-family: Inter, 'Segoe UI', Roboto, system-ui, -apple-system, sans-serif;
  }
  :global(*) { box-sizing: border-box; }
  main { max-width: 900px; margin: 0 auto; padding: 28px 18px 40px; }
  .brand { color: #f6f8ff; text-decoration: none; font-weight: 700; font-size: 1.1rem; }
  form { display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 10px; }
  input {
    width: 100%; border: 1px solid #334a82; background: #121b30; color: #f4f6fd;
    border-radius: 10px; padding: 11px 12px; font-size: 1rem;
  }
  input:focus, button:focus, a:focus { outline: 2px solid #6f96ff; outline-offset: 1px; }
  button {
    border: 1px solid #4a6fd0; background: #2a4181; color: #f6f8ff;
    border-radius: 10px; padding: 10px 14px; font-weight: 600; cursor: pointer;
  }
  .hero {
    min-height: calc(100vh - 120px);
    text-align: center;
    display: grid;
    align-content: center;
    justify-items: center;
    gap: 14px;
  }
  .hero-form { width: min(100%, 640px); }
  .results-header { display: grid; gap: 12px; margin-bottom: 18px; }
  .results-form { max-width: 640px; }
  h1 { margin: 0; font-size: 2rem; }
  p { margin: 0; color: #c5d0ee; line-height: 1.45; }
  .results-head { margin-bottom: 14px; display: grid; gap: 6px; }
  .results-list { display: grid; gap: 10px; }
  article { border: 1px solid #283c6d; background: #111a2d; border-radius: 12px; padding: 12px; }
  .top-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
  .type { font-size: 0.78rem; color: #b8c9f5; }
  .url { color: #9cb6f5; text-decoration: none; font-size: 0.87rem; }
  h2 { margin: 6px 0; font-size: 1.04rem; }
  h2 a { color: #eef3ff; text-decoration: none; }
  .empty { margin-top: 10px; }
  .sr-only {
    position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
    overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
  }
</style>
