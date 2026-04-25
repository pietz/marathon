<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import { base } from '$app/paths';
	import 'leaflet/dist/leaflet.css';

	type SearchResult = {
		id: string;
		bib: string | null;
		fullName: string;
		firstName: string;
		lastName: string;
		club: string | null;
		sex: string | null;
	};

	type Runner = {
		id: string;
		bib: string | null;
		fullName: string | null;
		firstName: string;
		lastName: string;
		club: string | null;
		status: string;
		km: number;
		speedKmh: number | null;
		source: string | null;
		coordinate: [number, number] | null;
	};

	type RunnerView = Runner & { color: string };

	// Tuned for the warm voyager basemap: saturated enough to read on top
	// of pastel land/water but not neon. Each pair is visually distinct.
	const PALETTE = [
		'#d44a4a', // red
		'#e08a1a', // amber
		'#3a8e3a', // green
		'#1f8f88', // teal
		'#2c6db8', // blue
		'#6a4ec2', // violet
		'#c4499a', // magenta
		'#a85e2a', // rust
		'#7d7e25', // olive
		'#3a6f5a', // moss
		'#9b3a3a', // brick
		'#4a4f5a'  // slate
	];
	const MAX_RUNNERS = 12;
	const POLL_MS = 15_000;
	const SEARCH_DEBOUNCE_MS = 1000;

	// State
	let query = $state('');
	let searching = $state(false);
	let results = $state<SearchResult[]>([]);
	let dropdownOpen = $state(false);
	let activeIdx = $state(-1);

	let selected = $state<RunnerView[]>([]);
	let activeId = $state<string | null>(null);
	let lastUpdate = $state<string | null>(null);

	let mapEl: HTMLDivElement;
	let map: any;
	let L: any;
	let routeLayer: any;
	let routeGlowLayer: any;
	const markerLayer = new Map<string, any>();
	let pollHandle: ReturnType<typeof setInterval> | null = null;
	let searchTimer: ReturnType<typeof setTimeout> | null = null;

	// ---- URL sync ----------------------------------------------------------
	function readBibsFromURL(): string[] {
		if (!browser) return [];
		const p = new URLSearchParams(window.location.search);
		const raw = p.get('bibs') || '';
		return raw.split(',').map((s) => s.trim()).filter(Boolean).slice(0, MAX_RUNNERS);
	}

	function writeBibsToURL(bibs: string[]) {
		if (!browser) return;
		const url = new URL(window.location.href);
		if (bibs.length) url.searchParams.set('bibs', bibs.join(','));
		else url.searchParams.delete('bibs');
		window.history.replaceState({}, '', url);
	}

	// ---- Color management --------------------------------------------------
	function nextFreeColor(): string {
		const used = new Set(selected.map((r) => r.color));
		for (const c of PALETTE) if (!used.has(c)) return c;
		return PALETTE[selected.length % PALETTE.length];
	}

	// ---- API ---------------------------------------------------------------
	async function searchAPI(q: string): Promise<SearchResult[]> {
		const r = await fetch(`${base}/api/search?q=${encodeURIComponent(q)}`);
		if (!r.ok) throw new Error(`search ${r.status}`);
		const data = await r.json();
		return data.results || [];
	}

	async function fetchRoute() {
		try {
			const r = await fetch(`${base}/api/route`);
			if (!r.ok) throw new Error(`route ${r.status}`);
			const { route } = (await r.json()) as { route: [number, number][] };
			drawRoute(route);
		} catch (e) {
			console.error('route fetch failed', e);
		}
	}

	async function fetchRunners(bibs: string[]): Promise<{ lastUpdate: string; runners: Runner[] }> {
		if (!bibs.length) return { lastUpdate: '', runners: [] };
		const r = await fetch(`${base}/api/runners?bibs=${bibs.join(',')}`);
		if (!r.ok) throw new Error(`runners ${r.status}`);
		return r.json();
	}

	async function refreshRunners() {
		if (!selected.length) return;
		try {
			const { lastUpdate: ts, runners } = await fetchRunners(
				selected.map((r) => r.bib).filter((b): b is string => !!b)
			);
			const byBib = new Map(runners.map((r) => [r.bib, r]));
			selected = selected.map((cur) => {
				const fresh = cur.bib ? byBib.get(cur.bib) : undefined;
				return fresh ? { ...cur, ...fresh } : cur;
			});
			lastUpdate = ts;
			renderMarkers();
		} catch (e) {
			console.error('runners fetch failed', e);
		}
	}

	// ---- Selection actions -------------------------------------------------
	async function addRunner(r: SearchResult) {
		if (!r.bib) return;
		if (selected.some((x) => x.bib === r.bib)) {
			closeDropdown();
			return;
		}
		if (selected.length >= MAX_RUNNERS) return;
		const view: RunnerView = {
			id: r.id,
			bib: r.bib,
			fullName: r.fullName,
			firstName: r.firstName,
			lastName: r.lastName,
			club: r.club,
			status: 'unknown',
			km: 0,
			speedKmh: null,
			source: null,
			coordinate: null,
			color: nextFreeColor()
		};
		selected = [...selected, view];
		writeBibsToURL(selected.map((x) => x.bib!).filter(Boolean));
		closeDropdown();
		query = '';
		results = [];
		await refreshRunners();
		focusOn(r.bib, { center: true });
	}

	function removeRunner(bib: string) {
		selected = selected.filter((r) => r.bib !== bib);
		writeBibsToURL(selected.map((x) => x.bib!).filter(Boolean));
		if (activeId === bib) activeId = null;
		const m = markerLayer.get(bib);
		if (m) {
			map.removeLayer(m);
			markerLayer.delete(bib);
		}
	}

	function focusOn(bib: string, opts: { center?: boolean } = {}) {
		activeId = bib;
		const r = selected.find((s) => s.bib === bib);
		if (r?.coordinate && map && opts.center) {
			map.flyTo(r.coordinate, Math.max(map.getZoom(), 14), { duration: 0.6 });
		}
		renderMarkers();
	}

	// ---- Search ------------------------------------------------------------
	function onQueryInput() {
		if (searchTimer) clearTimeout(searchTimer);
		const q = query.trim();
		if (q.length < 2) {
			results = [];
			searching = false;
			dropdownOpen = false;
			return;
		}
		searching = true;
		dropdownOpen = true;
		searchTimer = setTimeout(async () => {
			try {
				results = await searchAPI(q);
				activeIdx = results.length ? 0 : -1;
			} catch (e) {
				console.error(e);
				results = [];
			} finally {
				searching = false;
			}
		}, SEARCH_DEBOUNCE_MS);
	}

	function closeDropdown() {
		dropdownOpen = false;
		activeIdx = -1;
	}

	function onKeydown(e: KeyboardEvent) {
		if (!dropdownOpen || !results.length) {
			if (e.key === 'Escape') (e.target as HTMLElement).blur();
			return;
		}
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			activeIdx = (activeIdx + 1) % results.length;
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			activeIdx = (activeIdx - 1 + results.length) % results.length;
		} else if (e.key === 'Enter') {
			e.preventDefault();
			const r = results[activeIdx];
			if (r) addRunner(r);
		} else if (e.key === 'Escape') {
			closeDropdown();
			(e.target as HTMLElement).blur();
		}
	}

	// ---- Map ---------------------------------------------------------------
	function drawRoute(route: [number, number][]) {
		if (!map || !L || !route.length) return;
		if (routeGlowLayer) map.removeLayer(routeGlowLayer);
		if (routeLayer) map.removeLayer(routeLayer);
		// Subtle halo so the polyline reads on busy areas of the basemap
		routeGlowLayer = L.polyline(route, {
			color: '#ffffff',
			weight: 7,
			opacity: 0.55,
			lineCap: 'round',
			lineJoin: 'round'
		}).addTo(map);
		routeLayer = L.polyline(route, {
			color: '#1f1f24',
			weight: 2.6,
			opacity: 0.92,
			lineCap: 'round',
			lineJoin: 'round'
		}).addTo(map);
		map.fitBounds(routeLayer.getBounds(), { padding: [40, 40] });
	}

	function renderMarkers() {
		if (!map || !L) return;
		const bibs = new Set(selected.map((r) => r.bib).filter(Boolean) as string[]);
		for (const [bib, m] of markerLayer.entries()) {
			if (!bibs.has(bib)) {
				map.removeLayer(m);
				markerLayer.delete(bib);
			}
		}
		for (const r of selected) {
			if (!r.coordinate || !r.bib) continue;
			const isActive = r.bib === activeId;
			const html = `
				<span class="ring" style="--c: ${r.color}"></span>
				<span class="dot" style="background: ${r.color}"></span>
				<span class="lbl">${escapeHtml(r.firstName)}</span>
			`;
			const existing = markerLayer.get(r.bib);
			if (existing) {
				existing.setLatLng(r.coordinate);
				const el = existing.getElement();
				if (el) el.classList.toggle('is-active', isActive);
			} else {
				const icon = L.divIcon({
					className: `rm${isActive ? ' is-active' : ''}`,
					html,
					iconSize: [0, 0]
				});
				const m = L.marker(r.coordinate, { icon, zIndexOffset: isActive ? 1000 : 0 }).addTo(map);
				markerLayer.set(r.bib, m);
			}
		}
	}

	function escapeHtml(s: string) {
		return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c] || c);
	}

	// ---- Lifecycle ---------------------------------------------------------
	onMount(async () => {
		L = (await import('leaflet')).default;
		map = L.map(mapEl, { zoomControl: false, attributionControl: true })
			.setView([53.55, 9.99], 12);
		L.control.zoom({ position: 'topright' }).addTo(map);

		L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
			subdomains: 'abcd',
			maxZoom: 19,
			attribution:
				'&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>'
		}).addTo(map);

		await fetchRoute();

		const urlBibs = readBibsFromURL();
		if (urlBibs.length) {
			selected = urlBibs.map((bib, i) => ({
				id: '',
				bib,
				fullName: null,
				firstName: '…',
				lastName: '',
				club: null,
				status: 'unknown',
				km: 0,
				speedKmh: null,
				source: null,
				coordinate: null,
				color: PALETTE[i % PALETTE.length]
			}));
			await refreshRunners();
		}

		pollHandle = setInterval(refreshRunners, POLL_MS);
	});

	onDestroy(() => {
		if (pollHandle) clearInterval(pollHandle);
		if (searchTimer) clearTimeout(searchTimer);
		if (map) map.remove();
	});

	function onDocClick(e: MouseEvent) {
		const t = e.target as HTMLElement;
		if (!t.closest('.search-shell')) closeDropdown();
	}

	$effect(() => {
		if (!browser) return;
		document.addEventListener('click', onDocClick);
		return () => document.removeEventListener('click', onDocClick);
	});

	function fmtKm(km: number) {
		return km.toFixed(1).replace('.', ',') + ' km';
	}
</script>

<svelte:head>
	<title>Marathon Tracking · Hamburg 2026</title>
	<meta name="theme-color" content="#f7f5f0" />
	<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
	<link
		rel="stylesheet"
		href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"
	/>
</svelte:head>

<div class="page">
	<header class="topbar">
		<div class="search-shell" role="combobox" aria-haspopup="listbox" aria-expanded={dropdownOpen}>
			<svg class="search-icon" viewBox="0 0 20 20" aria-hidden="true">
				<circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="1.6" />
				<line x1="13.5" y1="13.5" x2="17" y2="17" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
			</svg>
			<input
				bind:value={query}
				oninput={onQueryInput}
				onkeydown={onKeydown}
				onfocus={() => { if (results.length) dropdownOpen = true; }}
				type="text"
				class="search"
				placeholder="Nachname oder Startnummer"
				aria-label="Läufer:innen suchen"
				aria-autocomplete="list"
				autocomplete="off"
				autocapitalize="off"
				autocorrect="off"
				spellcheck="false"
			/>

			{#if dropdownOpen}
				<div class="dropdown" role="listbox">
					{#if searching}
						<div class="hint">Sucht…</div>
					{:else if !results.length && query.trim().length >= 2}
						<div class="hint">Keine Treffer</div>
					{:else}
						{#each results as r, i (r.id)}
							{@const taken = selected.some((s) => s.bib === r.bib)}
							<button
								type="button"
								class="result"
								class:active={i === activeIdx}
								class:taken
								role="option"
								aria-selected={i === activeIdx}
								onclick={() => addRunner(r)}
								onmouseenter={() => (activeIdx = i)}
							>
								<span class="result-name">{r.fullName}</span>
								<span class="result-bib">#{r.bib}</span>
								{#if r.club}<span class="result-club">{r.club}</span>{/if}
								{#if taken}<span class="result-taken">ausgewählt</span>{/if}
							</button>
						{/each}
					{/if}
				</div>
			{/if}
		</div>
	</header>

	<section class="subbar">
		{#if selected.length}
			<div class="chip-track">
				{#each selected as r (r.bib)}
					<div
						class="chip"
						class:is-active={activeId === r.bib}
						style="--c: {r.color}"
					>
						<button
							type="button"
							class="chip-body"
							onclick={() => r.bib && focusOn(r.bib, { center: true })}
							aria-label="Auf {r.firstName} zentrieren"
						>
							<span class="chip-dot"></span>
							<span class="chip-name">{r.firstName || r.lastName || '…'}</span>
							<span class="chip-km">{fmtKm(r.km)}</span>
						</button>
						<button
							type="button"
							class="chip-x"
							onclick={() => r.bib && removeRunner(r.bib)}
							aria-label="{r.firstName} entfernen"
						>
							<svg viewBox="0 0 14 14" aria-hidden="true">
								<line x1="3" y1="3" x2="11" y2="11" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
								<line x1="11" y1="3" x2="3" y2="11" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
							</svg>
						</button>
					</div>
				{/each}
			</div>
		{:else}
			<p class="title">
				Verfolge Läufer:innen beim
				<span class="title-strong">Hamburg Marathon 2026</span>
			</p>
		{/if}
	</section>

	<main class="map-wrap">
		<div bind:this={mapEl} class="map"></div>

		{#if lastUpdate && selected.length}
			<div class="updated">
				<span class="pulse"></span>
				Aktualisiert {new Date(lastUpdate).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })}
			</div>
		{/if}
	</main>
</div>

<style>
	:global(html, body) {
		margin: 0;
		padding: 0;
		background: #f7f5f0;
		color: #1a1d23;
		font-family: 'Inter Tight', system-ui, -apple-system, sans-serif;
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
	}

	.page {
		--bg: #f7f5f0;
		--surface: #ffffff;
		--surface-2: #f1ede5;
		--hairline: rgba(0, 0, 0, 0.08);
		--hairline-strong: rgba(0, 0, 0, 0.14);
		--ink: #1a1d23;
		--pebble: #5a6068;
		--fog: #9aa0a8;
		--accent: #1a1d23;
		--accent-soft: rgba(26, 29, 35, 0.08);

		--font-ui: 'Inter Tight', system-ui, sans-serif;
		--font-mono: 'JetBrains Mono', ui-monospace, monospace;

		display: flex;
		flex-direction: column;
		height: 100dvh;
		background: var(--bg);
		overflow: hidden;
	}

	/* ---- top bar ---- */
	.topbar {
		padding: 10px 16px;
		border-bottom: 1px solid var(--hairline);
		background: rgba(247, 245, 240, 0.92);
		backdrop-filter: saturate(140%) blur(10px);
		-webkit-backdrop-filter: saturate(140%) blur(10px);
		z-index: 1000;
		flex-shrink: 0;
	}

	/* ---- search ---- */
	.search-shell {
		position: relative;
		min-width: 0;
		max-width: 480px;
		margin: 0 auto;
	}
	.search-icon {
		position: absolute;
		left: 12px;
		top: 50%;
		transform: translateY(-50%);
		width: 16px;
		height: 16px;
		color: var(--pebble);
		pointer-events: none;
	}
	.search {
		width: 100%;
		height: 42px;
		padding: 0 14px 0 36px;
		background: var(--surface);
		border: 1px solid var(--hairline-strong);
		border-radius: 10px;
		color: var(--ink);
		font: 500 16px/1 var(--font-ui);
		transition: border-color 140ms ease, box-shadow 140ms ease;
	}
	.search:focus {
		outline: none;
		border-color: var(--ink);
		box-shadow: 0 0 0 3px var(--accent-soft);
	}
	.search::placeholder { color: var(--fog); }

	.dropdown {
		position: absolute;
		top: calc(100% + 6px);
		left: 0;
		right: 0;
		max-height: min(360px, 60dvh);
		overflow-y: auto;
		overscroll-behavior: contain;
		background: var(--surface);
		border: 1px solid var(--hairline-strong);
		border-radius: 10px;
		box-shadow: 0 10px 32px rgba(0, 0, 0, 0.12);
		animation: drop 160ms ease;
	}
	@keyframes drop {
		from { opacity: 0; transform: translateY(-4px); }
		to   { opacity: 1; transform: translateY(0); }
	}
	.hint {
		padding: 16px;
		color: var(--fog);
		font-size: 13px;
	}
	.result {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		grid-auto-rows: auto;
		column-gap: 12px;
		row-gap: 2px;
		width: 100%;
		padding: 12px 14px;
		background: transparent;
		border: 0;
		border-bottom: 1px solid var(--hairline);
		text-align: left;
		cursor: pointer;
		color: var(--ink);
	}
	.result:last-child { border-bottom: 0; }
	.result.active { background: var(--surface-2); }
	.result.taken { opacity: 0.5; cursor: default; }
	.result.taken:hover { background: transparent; }
	.result-name {
		font: 500 15px/1.25 var(--font-ui);
	}
	.result-bib {
		font: 500 13px/1 var(--font-mono);
		color: var(--pebble);
		font-variant-numeric: tabular-nums;
		align-self: center;
	}
	.result-club {
		grid-column: 1;
		font: 400 12px/1.3 var(--font-ui);
		color: var(--fog);
	}
	.result-taken {
		grid-column: 2;
		font: 500 11px/1 var(--font-ui);
		color: var(--pebble);
		letter-spacing: 0.04em;
		text-transform: uppercase;
	}

	/* ---- map ---- */
	.map-wrap {
		position: relative;
		flex: 1 1 auto;
		min-height: 0;
		background: var(--bg);
	}
	.map {
		position: absolute;
		inset: 0;
	}
	:global(.leaflet-container) {
		background: #e8eaed;
		font-family: var(--font-ui);
	}
	:global(.leaflet-control-attribution) {
		background: rgba(255, 255, 255, 0.85) !important;
		color: var(--pebble) !important;
		font-size: 10px !important;
	}
	:global(.leaflet-control-zoom a) {
		background: var(--surface) !important;
		color: var(--ink) !important;
		border: 1px solid var(--hairline-strong) !important;
		display: grid !important;
		place-items: center !important;
		font-size: 18px !important;
		line-height: 1 !important;
		font-family: var(--font-ui) !important;
		padding: 0 !important;
	}
	:global(.leaflet-control-zoom a:hover) {
		background: var(--surface-2) !important;
	}

	/* ---- last-update pill ---- */
	.updated {
		position: absolute;
		top: 12px;
		left: 50%;
		transform: translateX(-50%);
		display: inline-flex;
		align-items: center;
		gap: 6px;
		padding: 5px 10px 5px 8px;
		background: rgba(255, 255, 255, 0.9);
		backdrop-filter: blur(8px);
		border: 1px solid var(--hairline);
		border-radius: 999px;
		font: 500 11px/1 var(--font-ui);
		color: var(--pebble);
		letter-spacing: 0.02em;
		pointer-events: none;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
	}
	.updated .pulse {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: #2c8a2c;
		box-shadow: 0 0 0 0 rgba(44, 138, 44, 0.4);
		animation: pulse-dot 2.4s ease-out infinite;
	}
	@keyframes pulse-dot {
		0%   { box-shadow: 0 0 0 0 rgba(44, 138, 44, 0.4); }
		100% { box-shadow: 0 0 0 8px rgba(44, 138, 44, 0); }
	}

	/* ---- subbar (title or chips) ---- */
	.subbar {
		flex-shrink: 0;
		min-height: 56px;
		display: flex;
		align-items: center;
		border-bottom: 1px solid var(--hairline);
		background: var(--bg);
	}
	.title {
		margin: 0;
		padding: 14px 16px;
		font: 400 13px/1.4 var(--font-ui);
		color: var(--pebble);
		text-align: center;
		width: 100%;
	}
	.title-strong {
		display: inline;
		color: var(--ink);
		font-weight: 600;
	}
	@media (min-width: 480px) {
		.title { font-size: 14px; }
	}

	.chip-track {
		display: flex;
		gap: 8px;
		overflow-x: auto;
		overscroll-behavior-x: contain;
		scroll-snap-type: x proximity;
		padding: 12px 16px;
		scrollbar-width: none;
		width: 100%;
	}
	.chip-track::-webkit-scrollbar { display: none; }

	.chip {
		display: inline-flex;
		align-items: center;
		flex-shrink: 0;
		background: var(--surface);
		border: 1px solid var(--hairline-strong);
		border-radius: 999px;
		scroll-snap-align: start;
		transition: border-color 160ms ease, box-shadow 160ms ease;
		animation: chip-in 220ms ease both;
		box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
	}
	@keyframes chip-in {
		from { opacity: 0; transform: translateY(6px); }
		to   { opacity: 1; transform: translateY(0); }
	}
	.chip.is-active {
		border-color: var(--c);
		box-shadow: 0 0 0 1px var(--c) inset, 0 4px 14px -4px var(--c);
	}
	.chip-body {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		padding: 8px 4px 8px 12px;
		background: transparent;
		border: 0;
		color: var(--ink);
		cursor: pointer;
		font: 500 13px/1 var(--font-ui);
	}
	.chip-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--c);
		flex-shrink: 0;
	}
	.chip-name {
		max-width: 96px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.chip-km {
		font: 500 13px/1 var(--font-mono);
		color: var(--pebble);
		font-variant-numeric: tabular-nums;
	}
	.chip.is-active .chip-km { color: var(--ink); }
	.chip-x {
		display: inline-grid;
		place-items: center;
		width: 28px;
		height: 28px;
		margin-right: 4px;
		background: transparent;
		border: 0;
		border-radius: 50%;
		color: var(--fog);
		cursor: pointer;
		transition: color 140ms ease, background 140ms ease;
	}
	.chip-x:hover {
		color: var(--ink);
		background: var(--surface-2);
	}
	.chip-x svg {
		width: 14px;
		height: 14px;
	}

	/* ---- runner markers ---- */
	:global(.rm) {
		position: relative;
	}
	:global(.rm .dot) {
		position: absolute;
		left: -7px;
		top: -7px;
		width: 14px;
		height: 14px;
		border-radius: 50%;
		box-shadow: 0 0 0 2px #ffffff, 0 1px 4px rgba(0, 0, 0, 0.35);
		z-index: 2;
	}
	:global(.rm .ring) {
		position: absolute;
		left: -11px;
		top: -11px;
		width: 22px;
		height: 22px;
		border-radius: 50%;
		border: 2px solid var(--c);
		opacity: 0;
		transition: opacity 200ms ease;
		z-index: 1;
	}
	:global(.rm.is-active .ring) {
		opacity: 1;
		animation: marker-pulse 1.6s ease-out infinite;
	}
	@keyframes marker-pulse {
		0%   { transform: scale(1);   opacity: 0.8; }
		100% { transform: scale(2.4); opacity: 0;   }
	}
	:global(.rm .lbl) {
		position: absolute;
		left: 12px;
		top: -7px;
		font: 600 11px/1 'Inter Tight', system-ui, sans-serif;
		color: #1a1d23;
		text-shadow: 0 0 4px #ffffff, 0 0 2px #ffffff, 0 0 2px #ffffff;
		white-space: nowrap;
		letter-spacing: 0.01em;
		z-index: 3;
	}
</style>
