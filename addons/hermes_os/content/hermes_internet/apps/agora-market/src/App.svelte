<script>
  import { listings } from './listings';

  const START_BALANCE = 250;
  let balance = START_BALANCE;
  let inventory = [];
  let transactions = [];
  let messages = [];
  let selectedListingId = null;

  const riskTone = {
    Low: 'risk-low',
    Medium: 'risk-mid',
    High: 'risk-high'
  };

  $: selectedListing = listings.find((entry) => entry.id === selectedListingId) || null;

  function formatDollars(value) {
    return `$${value}`;
  }

  function inspect(listingId) {
    const listing = listings.find((entry) => entry.id === listingId);
    if (!listing) {
      pushMessage(`Listing not found: ${listingId}`);
      return;
    }

    selectedListingId = listing.id;
    pushMessage(`Inspected ${listing.name}.`);
  }

  function buy(listingId) {
    const listing = listings.find((entry) => entry.id === listingId);
    if (!listing) {
      pushMessage(`Purchase failed. Listing not found: ${listingId}`);
      return;
    }

    if (inventory.includes(listing.name)) {
      pushMessage(`Purchase blocked. You already own ${listing.name}.`);
      return;
    }

    if (balance < listing.price) {
      pushMessage(`Purchase failed for ${listing.name}. Insufficient funds.`);
      return;
    }

    balance -= listing.price;
    inventory = [listing.name, ...inventory];
    transactions = [`RECEIPT: Bought ${listing.name} for ${formatDollars(listing.price)} from ${listing.seller}.`, ...transactions];
    pushMessage(`Purchase complete: ${listing.name} (-${formatDollars(listing.price)}).`);
  }

  function pushMessage(text) {
    messages = [text, ...messages.slice(0, 7)];
  }

  function resetMarket() {
    balance = START_BALANCE;
    inventory = [];
    transactions = [];
    messages = [];
    selectedListingId = null;
  }
</script>

<main>
  <section class="hero panel-glass">
    <div>
      <p class="kicker">WorldWeb Marketplace</p>
      <h1>Agora Market</h1>
      <p class="subtitle">Buy trusted finds with dollars only. Start with $250 and build your inventory.</p>
    </div>
    <div class="wallet-panel">
      <span class="wallet-label">Wallet Balance</span>
      <strong>{formatDollars(balance)}</strong>
      <p class="wallet-sub">Starting balance: {formatDollars(START_BALANCE)}</p>
      <button class="ghost" on:click={resetMarket}>Reset session</button>
    </div>
  </section>

  <section class="market-layout">
    <section class="panel listings-panel">
      <div class="panel-heading">
        <h2>Listings</h2>
        <span>{listings.length} available</span>
      </div>

      <div class="listings-grid">
        {#each listings as item}
          <article class:selected={selectedListingId === item.id} class="listing-card">
            <header>
              <div>
                <h3>{item.name}</h3>
                <p class="seller">{item.seller}</p>
              </div>
              <p class="price">{formatDollars(item.price)}</p>
            </header>

            <p class="details">{item.details}</p>

            <div class="meta-row">
              <span class="chip rep">Rep {item.reputation}</span>
              <span class="chip {riskTone[item.risk]}">{item.risk} risk</span>
            </div>

            <div class="actions">
              <button on:click={() => inspect(item.id)}>Inspect</button>
              <button class="buy" on:click={() => buy(item.id)} disabled={inventory.includes(item.name)}>Buy</button>
            </div>
          </article>
        {/each}
      </div>
    </section>

    <aside class="sidebar-column">
      <section class="panel detail-panel">
        <h2>Selected listing</h2>
        {#if selectedListing}
          <h3>{selectedListing.name}</h3>
          <p class="detail-price">{formatDollars(selectedListing.price)}</p>
          <p><strong>Seller:</strong> {selectedListing.seller}</p>
          <p><strong>Reputation:</strong> {selectedListing.reputation}</p>
          <p>
            <strong>Risk:</strong>
            <span class={riskTone[selectedListing.risk]}>{selectedListing.risk}</span>
          </p>
          <p>{selectedListing.details}</p>
        {:else}
          <p class="empty">Select Inspect on any listing to review full details before buying.</p>
        {/if}
      </section>

      <section class="panel">
        <h2>Inventory</h2>
        {#if inventory.length}
          <ul>
            {#each inventory as line}
              <li>{line}</li>
            {/each}
          </ul>
        {:else}
          <p class="empty">No purchases yet. Buy a listing to stock your inventory.</p>
        {/if}
      </section>

      <section class="panel">
        <h2>Receipts</h2>
        {#if transactions.length}
          <ul>
            {#each transactions as line}
              <li>{line}</li>
            {/each}
          </ul>
        {:else}
          <p class="empty">No receipts yet. Completed purchases will show here.</p>
        {/if}
      </section>

      <section class="panel">
        <h2>Messages</h2>
        {#if messages.length}
          <ul>
            {#each messages as line}
              <li>{line}</li>
            {/each}
          </ul>
        {:else}
          <p class="empty">No messages yet. Inspect or buy to generate updates.</p>
        {/if}
      </section>
    </aside>
  </section>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: Inter, 'Segoe UI', Roboto, system-ui, -apple-system, sans-serif;
    background: radial-gradient(circle at top left, #243262, #0b1020 55%);
    color: #eaf0ff;
  }

  :global(*) {
    box-sizing: border-box;
  }

  main {
    max-width: 1240px;
    margin: 0 auto;
    padding: 28px;
    display: grid;
    gap: 18px;
  }

  .panel {
    background: linear-gradient(180deg, #121b35, #0f1730);
    border: 1px solid #2e4278;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 18px 30px rgba(1, 8, 24, 0.3);
  }

  .panel-glass {
    backdrop-filter: blur(8px);
  }

  .hero {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 16px;
    align-items: center;
    padding: 20px;
  }

  .kicker {
    margin: 0 0 8px;
    color: #9fbae9;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.78rem;
    font-weight: 600;
  }

  h1 {
    margin: 0;
    font-size: 2rem;
    letter-spacing: 0.01em;
  }

  h2 {
    margin: 0 0 10px;
    font-size: 1.05rem;
  }

  .subtitle {
    margin: 8px 0 0;
    color: #c5d4fa;
    line-height: 1.4;
    max-width: 56ch;
  }

  .wallet-panel {
    border: 1px solid #34529a;
    border-radius: 14px;
    background: #0b142d;
    padding: 12px 14px;
    min-width: 220px;
    display: grid;
    gap: 4px;
  }

  .wallet-label,
  .wallet-sub {
    color: #9eb3e3;
    margin: 0;
    font-size: 0.86rem;
  }

  .wallet-panel strong {
    color: #95ffc6;
    font-size: 1.7rem;
    line-height: 1;
  }

  .market-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.7fr) minmax(320px, 1fr);
    gap: 16px;
  }

  .panel-heading {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 10px;
  }

  .panel-heading span {
    font-size: 0.9rem;
    color: #9db2e3;
  }

  .listings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
    gap: 12px;
  }

  .listing-card {
    border: 1px solid #355091;
    border-radius: 12px;
    background: #0c1430;
    padding: 12px;
    display: grid;
    gap: 10px;
    transition: border-color 120ms ease, transform 120ms ease;
  }

  .listing-card:hover {
    border-color: #4f71ca;
    transform: translateY(-1px);
  }

  .listing-card.selected {
    border-color: #79a5ff;
    box-shadow: inset 0 0 0 1px #79a5ff;
  }

  .listing-card header {
    display: flex;
    justify-content: space-between;
    gap: 10px;
  }

  .listing-card h3 {
    margin: 0;
    font-size: 1rem;
  }

  .seller {
    margin: 2px 0 0;
    color: #acc2f2;
    font-size: 0.86rem;
  }

  .price,
  .detail-price {
    margin: 0;
    color: #94ffc3;
    font-weight: 700;
  }

  .details {
    margin: 0;
    color: #d2ddfc;
    line-height: 1.35;
    font-size: 0.92rem;
  }

  .meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .chip {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    border: 1px solid #4a62a6;
    padding: 2px 9px;
    font-size: 0.8rem;
    color: #dce5ff;
    background: #1d2d56;
  }

  .actions {
    display: flex;
    gap: 8px;
  }

  button {
    background: #273f7a;
    color: #f3f6ff;
    border: 1px solid #496cc4;
    border-radius: 9px;
    padding: 6px 10px;
    cursor: pointer;
    font-weight: 600;
  }

  button:hover {
    filter: brightness(1.08);
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  button.buy {
    background: #245f3c;
    border-color: #3fa070;
  }

  button.ghost {
    background: transparent;
    border-color: #3f5f9e;
  }

  .sidebar-column {
    display: grid;
    gap: 12px;
    align-content: start;
  }

  .detail-panel h3 {
    margin: 0;
    font-size: 1.08rem;
  }

  .detail-panel p {
    margin: 6px 0 0;
    color: #d3defb;
  }

  ul {
    margin: 0;
    padding-left: 18px;
    display: grid;
    gap: 5px;
  }

  li {
    color: #d7e0ff;
    line-height: 1.3;
  }

  .empty {
    margin: 0;
    color: #aebfe8;
    font-size: 0.93rem;
    line-height: 1.35;
  }

  .risk-low {
    color: #8ff7bc;
  }

  .risk-mid {
    color: #ffd48d;
  }

  .risk-high {
    color: #ff9a9a;
  }

  @media (max-width: 980px) {
    main {
      padding: 18px;
    }

    .hero {
      grid-template-columns: 1fr;
    }

    .market-layout {
      grid-template-columns: 1fr;
    }
  }
</style>
