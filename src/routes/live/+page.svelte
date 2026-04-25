<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { base } from '$app/paths';
	import 'leaflet/dist/leaflet.css';

	type Runner = {
		id: string;
		name: string;
		bib: string;
		color: string;
		fullName: string | null;
		status: string;
		km: number;
		speedKmh: number | null;
		source: string | null;
		lastChange: string | null;
		validUntilKm: number | null;
		coordinate: [number, number] | null;
		splits: { name: string; km: number | string; time: string; kmh: number | string | null }[];
	};

	type Live = {
		lastUpdate: string | null;
		route: [number, number][];
		runners: Runner[];
	};

	const POLL_MS = 15_000;

	let live = $state<Live | null>(null);
	let error = $state<string | null>(null);
	let loading = $state(true);

	let mapEl: HTMLDivElement;
	let map: any;
	let L: any;
	let routeLayer: any;
	const markers = new Map<string, any>();
	let pollHandle: ReturnType<typeof setInterval> | null = null;

	const STATUS_LABEL: Record<string, string> = {
		not_started: 'Noch nicht gestartet',
		running: 'Läuft',
		finished: 'Im Ziel',
		stopped: 'Gestoppt',
		unknown: 'Unbekannt'
	};

	function fmtKm(km: number) {
		return `${km.toFixed(1)} km`;
	}

	function lastSplit(r: Runner) {
		return r.splits.length ? r.splits[r.splits.length - 1] : null;
	}

	async function fetchLive() {
		try {
			const res = await fetch(`${base}/api/live`, { cache: 'no-store' });
			if (!res.ok) throw new Error(`HTTP ${res.status}`);
			const data = (await res.json()) as Live;
			live = data;
			error = null;
			renderMap();
		} catch (e) {
			error = e instanceof Error ? e.message : String(e);
		} finally {
			loading = false;
		}
	}

	function renderMap() {
		if (!map || !L || !live) return;

		// Route polyline (only need to draw once)
		if (!routeLayer && live.route.length) {
			routeLayer = L.polyline(live.route, {
				color: '#ffffff',
				weight: 3,
				opacity: 0.55
			}).addTo(map);
			map.fitBounds(routeLayer.getBounds(), { padding: [40, 40] });
		}

		// Runner markers
		for (const r of live.runners) {
			if (!r.coordinate) continue;
			const existing = markers.get(r.id);
			if (existing) {
				existing.setLatLng(r.coordinate);
			} else {
				const icon = L.divIcon({
					className: 'runner-marker',
					html: `<span class="dot" style="background:${r.color}"></span><span class="label">${r.name}</span>`,
					iconSize: [0, 0]
				});
				const m = L.marker(r.coordinate, { icon }).addTo(map);
				markers.set(r.id, m);
			}
		}
	}

	onMount(async () => {
		L = (await import('leaflet')).default;
		map = L.map(mapEl, {
			zoomControl: true,
			attributionControl: true
		}).setView([53.55, 9.99], 13);

		L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png', {
			attribution:
				'&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
			subdomains: 'abcd',
			maxZoom: 19
		}).addTo(map);

		await fetchLive();
		pollHandle = setInterval(fetchLive, POLL_MS);
	});

	onDestroy(() => {
		if (pollHandle) clearInterval(pollHandle);
		if (map) map.remove();
	});
</script>

<svelte:head>
	<title>Live · Marathon Hamburg 2026</title>
</svelte:head>

<div class="page">
	<header>
		<a class="back" href="{base}/">← Zurück</a>
		<h1>Live Tracking</h1>
		<span class="updated">
			{#if live?.lastUpdate}
				Update: {new Date(live.lastUpdate).toLocaleTimeString('de-DE')}
			{:else if loading}
				Lade…
			{/if}
		</span>
	</header>

	<div class="map-wrap">
		<div bind:this={mapEl} class="map"></div>
		{#if error}
			<div class="error">Fehler: {error}</div>
		{/if}
	</div>

	<aside class="panel">
		{#if live}
			{#each live.runners as r (r.id)}
				{@const split = lastSplit(r)}
				<div class="card" style="--c:{r.color}">
					<div class="row">
						<span class="dot" style="background:{r.color}"></span>
						<span class="name">{r.name}</span>
						<span class="bib">#{r.bib}</span>
					</div>
					<div class="row meta">
						<span class="status">{STATUS_LABEL[r.status] ?? r.status}</span>
						<span class="km">{fmtKm(r.km)}</span>
					</div>
					{#if split}
						<div class="row split">
							<span>{split.name}: {split.time}</span>
							{#if split.kmh}<span>{split.kmh} km/h</span>{/if}
						</div>
					{/if}
				</div>
			{/each}
		{:else if loading}
			<div class="loading">Lade Live-Daten…</div>
		{/if}
	</aside>
</div>

<style>
	.page {
		display: grid;
		grid-template-columns: 1fr 320px;
		grid-template-rows: auto 1fr;
		height: 100vh;
		gap: 0;
	}

	header {
		grid-column: 1 / -1;
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 0.75rem 1.25rem;
		background: rgba(10, 10, 26, 0.85);
		border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	}

	.back {
		color: #aaa;
		text-decoration: none;
		font-size: 0.85rem;
	}
	.back:hover {
		color: white;
	}

	header h1 {
		font-family: 'Press Start 2P', monospace;
		font-size: 0.95rem;
		flex: 1;
		letter-spacing: 0.05em;
	}

	.updated {
		font-size: 0.8rem;
		color: #888;
		font-variant-numeric: tabular-nums;
	}

	.map-wrap {
		position: relative;
		background: #0a0a1a;
		min-height: 0;
	}

	.map {
		width: 100%;
		height: 100%;
	}

	.error {
		position: absolute;
		top: 1rem;
		left: 50%;
		transform: translateX(-50%);
		background: rgba(231, 76, 60, 0.9);
		padding: 0.5rem 1rem;
		border-radius: 4px;
		font-size: 0.85rem;
		z-index: 1000;
	}

	.panel {
		background: rgba(10, 10, 26, 0.95);
		border-left: 1px solid rgba(255, 255, 255, 0.08);
		overflow-y: auto;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.card {
		background: rgba(255, 255, 255, 0.03);
		border: 1px solid rgba(255, 255, 255, 0.06);
		border-left: 4px solid var(--c);
		border-radius: 6px;
		padding: 0.75rem 0.9rem;
	}

	.row {
		display: flex;
		align-items: center;
		gap: 0.6rem;
	}

	.row + .row {
		margin-top: 0.35rem;
	}

	.dot {
		width: 0.7rem;
		height: 0.7rem;
		border-radius: 50%;
		display: inline-block;
		box-shadow: 0 0 8px currentColor;
	}

	.name {
		font-family: 'Press Start 2P', monospace;
		font-size: 0.78rem;
		flex: 1;
	}

	.bib {
		font-size: 0.75rem;
		color: #777;
		font-variant-numeric: tabular-nums;
	}

	.meta {
		justify-content: space-between;
		font-size: 0.85rem;
		color: #ccc;
	}

	.km {
		font-variant-numeric: tabular-nums;
		color: var(--c);
		font-weight: 600;
	}

	.split {
		font-size: 0.78rem;
		color: #888;
		justify-content: space-between;
	}

	.loading {
		color: #888;
		text-align: center;
		padding: 2rem 0;
	}

	@media (max-width: 720px) {
		.page {
			grid-template-columns: 1fr;
			grid-template-rows: auto 1fr auto;
		}

		.panel {
			flex-direction: row;
			border-left: none;
			border-top: 1px solid rgba(255, 255, 255, 0.08);
			max-height: 38vh;
			overflow-x: auto;
		}

		.card {
			min-width: 180px;
			flex-shrink: 0;
		}
	}

	:global(.runner-marker) {
		position: relative;
	}
	:global(.runner-marker .dot) {
		position: absolute;
		left: -9px;
		top: -9px;
		width: 18px;
		height: 18px;
		border-radius: 50%;
		border: 2px solid white;
		box-shadow:
			0 0 10px currentColor,
			0 2px 6px rgba(0, 0, 0, 0.5);
	}
	:global(.runner-marker .label) {
		position: absolute;
		left: 14px;
		top: -10px;
		font-family: 'Press Start 2P', monospace;
		font-size: 0.6rem;
		color: white;
		text-shadow: 0 0 4px black, 0 1px 2px black;
		white-space: nowrap;
	}
</style>
