<script lang="ts">
	import CharacterSelect from '$lib/components/CharacterSelect.svelte';
	import { audio } from '$lib/audio';
	import { onMount } from 'svelte';

	onMount(() => {
		audio.preload();
	});
</script>

<svelte:head>
	<title>Marathon 2026 — Choose Your Runner</title>
	<meta name="description" content="Choose your marathon runner — a fun character select for our 2026 marathon crew." />
</svelte:head>

<CharacterSelect />
