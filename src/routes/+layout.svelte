<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
	<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
</svelte:head>

{@render children()}

<style>
	:global(*) {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
	}

	:global(html, body) {
		background: #0a0a1a;
		color: white;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		overflow-x: hidden;
		min-height: 100vh;
	}

	:global(body) {
		background:
			radial-gradient(ellipse at 20% 50%, rgba(40, 20, 80, 0.4), transparent 50%),
			radial-gradient(ellipse at 80% 50%, rgba(20, 40, 80, 0.4), transparent 50%),
			radial-gradient(ellipse at 50% 100%, rgba(30, 30, 60, 0.6), transparent 50%),
			#0a0a1a;
	}
</style>
