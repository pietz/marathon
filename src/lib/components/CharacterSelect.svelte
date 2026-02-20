<script lang="ts">
	import { base } from '$app/paths';
	import { characters, type Character } from '$lib/data/characters';
	import CharacterComponent from './Character.svelte';
	import CharacterCard from './CharacterCard.svelte';

	let selectedCharacter = $state<Character | null>(null);

	function handleSelect(character: Character) {
		selectedCharacter = character;
	}

	function handleClose() {
		selectedCharacter = null;
	}

	// Character positions: parallelogram pattern
	// Lower row: Kevin, Jonas | Upper row: Tobi, Alex
	// Vector from lower→upper is the same (+11, +24) for both pairs
	const scenePositions = [
		{ x: 40, bottom: 33 },   // Tobi - upper left
		{ x: 27, bottom: 3 },    // Kevin - lower left
		{ x: 60, bottom: 3 },    // Jonas - lower right
		{ x: 73, bottom: 33 },   // Alex - upper right
	];
</script>

<div class="stage">
	<!-- Title -->
	<header class="title-area">
		<h1 class="title">
			<span class="title-sub">Choose Your</span>
			<span class="title-main">Runner</span>
		</h1>
		<p class="event-name">HAMBURG MARATHON 2026</p>
	</header>

	<!-- 3D Map + Characters scene -->
	<div class="scene">
		<!-- Tilted map image in the center background -->
		<div class="map-container">
			<div class="map-tilt">
				<img
					src="{base}/images/hamburg-map.png"
					alt="Hamburg map centered on the Alster"
					class="map-image"
				/>
			</div>
			<!-- Fade edges so the map blends into the background -->
			<div class="map-vignette"></div>
		</div>

		<!-- Characters positioned around the map -->
		{#each characters as character, i}
			{@const pos = scenePositions[i]}
			<div
				class="character-position"
				style="left: {pos.x}%; bottom: {pos.bottom}%; z-index: {100 - pos.bottom};"
			>
				<CharacterComponent
					{character}
					index={i}
					isSelected={selectedCharacter?.id === character.id}
					onSelect={handleSelect}
				/>
			</div>
		{/each}
	</div>

	<!-- Bottom bar -->
	<div class="bottom-bar">
		<div class="instruction desktop-only">
			<span class="key">HOVER</span> Preview
			<span class="separator">|</span>
			<span class="key">CLICK</span> Select
		</div>
		<div class="instruction mobile-only">
			<span class="key">TAP</span> Select
		</div>
	</div>
</div>

<!-- Character detail card -->
{#if selectedCharacter}
	<CharacterCard character={selectedCharacter} onClose={handleClose} />
{/if}

<style>
	.stage {
		position: relative;
		width: 100%;
		height: 100vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		overflow: hidden;
	}

	/* ---- Title ---- */
	.title-area {
		position: relative;
		z-index: 5;
		text-align: center;
		padding-top: 3vh;
		flex-shrink: 0;
	}

	.title {
		font-family: 'Press Start 2P', 'Courier New', monospace;
		font-size: clamp(1.2rem, 3.5vw, 2.2rem);
		color: white;
		text-transform: uppercase;
		margin: 0;
		line-height: 1.6;
		text-shadow:
			0 0 20px rgba(255, 255, 255, 0.3),
			0 0 60px rgba(100, 100, 255, 0.2);
	}

	.title-main {
		display: inline-block;
		background: linear-gradient(
			90deg,
			rgba(255, 255, 255, 0.95) 0%,
			rgba(120, 160, 255, 1) 25%,
			rgba(255, 255, 255, 1) 50%,
			rgba(120, 160, 255, 1) 75%,
			rgba(255, 255, 255, 0.95) 100%
		);
		background-size: 200% 100%;
		-webkit-background-clip: text;
		background-clip: text;
		-webkit-text-fill-color: transparent;
		animation: shimmer 3s linear infinite;
	}

	@keyframes shimmer {
		0% {
			background-position: 200% center;
		}
		100% {
			background-position: -200% center;
		}
	}

	.title-sub {
		display: block;
		font-size: 0.5em;
		color: rgba(255, 255, 255, 0.5);
		letter-spacing: 6px;
		margin-bottom: 0.25rem;
	}

	.event-name {
		font-family: 'Press Start 2P', 'Courier New', monospace;
		font-size: clamp(0.55rem, 1vw, 0.85rem);
		color: rgba(255, 200, 50, 0.6);
		letter-spacing: 6px;
		margin: 0.5rem 0 0 0;
	}

	/* ---- Scene with map + characters ---- */
	.scene {
		position: relative;
		flex: 1;
		width: 100%;
		margin: 0 auto;
	}

	/* Map container: spans the full scene */
	.map-container {
		position: absolute;
		inset: 0;
		z-index: 0;
		pointer-events: none;
		overflow: hidden;
	}

	.map-tilt {
		position: absolute;
		bottom: 0;
		left: 0;
		width: 100%;
		height: 160%;
		transform: perspective(1200px) rotateX(35deg) scale(1.3);
		transform-origin: center bottom;
	}

	.map-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
		object-position: center 70%;
		opacity: 0.55;
	}

	/* Vignette to fade map edges into the dark background */
	.map-vignette {
		position: absolute;
		inset: 0;
		background: radial-gradient(
			ellipse at 50% 70%,
			transparent 25%,
			rgba(10, 10, 26, 0.6) 50%,
			rgba(10, 10, 26, 0.95) 70%
		);
		pointer-events: none;
	}

	/* Character positions */
	.character-position {
		position: absolute;
		transform: translateX(-50%);
		z-index: 2;
	}

	/* ---- Bottom bar ---- */
	.bottom-bar {
		position: relative;
		z-index: 5;
		padding: 1rem 0 1.5rem;
		flex-shrink: 0;
	}

	.instruction {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.3);
		text-transform: uppercase;
		letter-spacing: 2px;
	}

	.key {
		display: inline-block;
		padding: 0.15rem 0.5rem;
		background: rgba(255, 255, 255, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.15);
		border-radius: 4px;
		font-family: 'Press Start 2P', 'Courier New', monospace;
		font-size: 0.55rem;
		margin-right: 0.25rem;
	}

	.separator {
		margin: 0 0.75rem;
		opacity: 0.3;
	}

	/* Mobile / desktop instruction toggle */
	.mobile-only {
		display: none;
	}

	@media (hover: none) and (pointer: coarse) {
		.desktop-only {
			display: none;
		}
		.mobile-only {
			display: block;
		}
	}
</style>
