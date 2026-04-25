<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { base } from '$app/paths';

	onMount(() => {
		if (!browser) return;
		const search = window.location.search || '';
		const hash = window.location.hash || '';
		window.location.replace(`${base}/live/${search}${hash}`);
	});
</script>

<svelte:head>
	<meta http-equiv="refresh" content={`0; url=${base}/live/`} />
	<title>Weiterleitung…</title>
</svelte:head>

<p style="font: 400 14px/1.5 system-ui, sans-serif; color: #98a0ad; padding: 24px; text-align: center;">
	Diese Seite wurde verschoben. Weiterleitung zu
	<a href="{base}/live/" style="color: #eef0f4;">/live</a>…
</p>
