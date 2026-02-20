<script lang="ts">
	import type { Character } from '$lib/data/characters';
	import { audio } from '$lib/audio';
	import PlaceholderAvatar from './PlaceholderAvatar.svelte';

	let {
		character,
		index,
		isSelected = false,
		onSelect
	}: {
		character: Character;
		index: number;
		isSelected?: boolean;
		onSelect: (character: Character) => void;
	} = $props();

	let isHovered = $state(false);
	let hasInteracted = $state(false);
	let rotation = $state(0);
	let animationFrame = $state<number | null>(null);
	let spinStartTime = $state<number | null>(null);

	function startSpin() {
		if (animationFrame) return;
		spinStartTime = performance.now();

		function animate(time: number) {
			const elapsed = time - (spinStartTime || time);
			// Starts slow, accelerates slightly, then decelerates smoothly into landing
			const duration = 900;
			const progress = Math.min(elapsed / duration, 1);
			// Custom curve: slow start, builds momentum, smooth stop
			// Using a sine-based ease that avoids any snap at the end
			const eased = progress < 0.3
				? (progress / 0.3) * (progress / 0.3) * 0.15  // slow start (0 → 0.15)
				: 0.15 + 0.85 * ((progress - 0.3) / 0.7);     // steady through to end
			// Apply smooth landing with sine
			const smoothed = eased < 1
				? eased - (Math.sin(eased * Math.PI * 2) * 0.01 * (1 - progress))
				: 1;
			rotation = smoothed * 360;

			if (progress < 1) {
				animationFrame = requestAnimationFrame(animate);
			} else {
				rotation = 360;
				// Reset to 0 on next frame to avoid visual jump
				requestAnimationFrame(() => {
					rotation = 0;
					animationFrame = null;
					spinStartTime = null;
				});
			}
		}
		animationFrame = requestAnimationFrame(animate);
	}

	async function ensureAudio() {
		if (!hasInteracted) {
			hasInteracted = true;
			await audio.init();
		}
	}

	async function handleMouseEnter() {
		isHovered = true;
		await ensureAudio();
		audio.playCharacterSound(index);
		startSpin();
	}

	function handleMouseLeave() {
		isHovered = false;
	}

	async function handleClick() {
		await ensureAudio();
		audio.playSelectSound(index);
		onSelect(character);
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			handleClick();
		}
	}


</script>

<button
	class="character-slot"
	class:hovered={isHovered}
	class:selected={isSelected}
	style="--char-color: {character.color}; --char-accent: {character.accentColor};"
	onmouseenter={handleMouseEnter}
	onmouseleave={handleMouseLeave}
	onclick={handleClick}
	onkeydown={handleKeydown}
	aria-label="Select {character.name}"
>
	<!-- Rising stone platform -->
	<div class="stone">
		<div class="stone-top"></div>
		<div class="stone-front"></div>
		<div class="stone-glow"></div>
	</div>

	<!-- Particles (behind character) -->
	<div class="particles back" aria-hidden="true">
		{#each Array(8) as _, i}
			<div class="particle" style="--i: {i}; --x: {(i * 31 + 7) % 100}; --y: {(i * 13 + 5) % 90}; --delay: {i * 0.12}s; --size: {2 + (i % 3) * 1.5}px;"></div>
		{/each}
	</div>

	<!-- Character container with 3D spin -->
	<div class="character-wrapper">
		<div class="character-3d" style="transform: rotateY({rotation}deg);">
			{#if character.imageFront}
				<img src={character.imageFront} alt={character.name} class="character-image" />
			{:else}
				<PlaceholderAvatar color={character.color} name={character.name} />
			{/if}
		</div>
	</div>

	<!-- Particles (in front of character) -->
	<div class="particles front" aria-hidden="true">
		{#each Array(6) as _, i}
			<div class="particle" style="--i: {i + 8}; --x: {(i * 43 + 19) % 100}; --y: {(i * 17 + 10) % 85}; --delay: {i * 0.15 + 0.05}s; --size: {1.5 + (i % 3)}px;"></div>
		{/each}
	</div>

	<!-- Name plate -->
	<div class="name-plate">
		<span class="name">{character.name}</span>
		<span class="subtitle">{character.subtitle}</span>
	</div>

	<!-- Spotlight effect -->
	<div class="spotlight"></div>
</button>

<style>
	.character-slot {
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: flex-end;
		padding: 1rem;
		padding-bottom: 0;
		cursor: pointer;
		perspective: 800px;
		border: none;
		background: transparent;
		outline: none;
		transition: filter 0.4s ease;
	}

	.character-slot:focus-visible {
		outline: 2px solid var(--char-color);
		outline-offset: 4px;
		border-radius: 12px;
	}

	/* The whole character + stone rises on hover */
	.character-wrapper {
		transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
	}

	.character-slot.hovered .character-wrapper {
		transform: translateY(clamp(-15px, -2vw, -30px));
	}

	.character-slot.hovered {
		z-index: 10;
		filter: brightness(1.15);
	}

	.character-slot.selected {
		z-index: 10;
		filter: brightness(1.15);
	}

	.character-slot.selected .character-wrapper {
		transform: translateY(clamp(-15px, -2vw, -30px));
	}

	/* 3D character container — scales with viewport */
	.character-3d {
		position: relative;
		width: clamp(105px, 10vw, 160px);
		height: clamp(210px, 20vw, 320px);
		transform-style: preserve-3d;
	}

	.character-image {
		width: 100%;
		height: 100%;
		object-fit: contain;
	}

	/* Stone platform that rises — scales with character */
	.stone {
		position: relative;
		width: clamp(60px, 7.5vw, 120px);
		height: clamp(7px, 0.9vw, 14px);
		margin-top: -6px;
		z-index: 1;
		transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1),
		            box-shadow 0.4s ease;
	}

	.character-slot.hovered .stone,
	.character-slot.selected .stone {
		transform: translateY(clamp(-15px, -2vw, -30px));
	}

	.stone-top {
		width: 100%;
		height: 100%;
		background: linear-gradient(
			to bottom,
			rgba(255, 255, 255, 0.12),
			rgba(255, 255, 255, 0.04)
		);
		border-radius: 50%;
		border: 1px solid rgba(255, 255, 255, 0.06);
	}

	.stone-front {
		position: absolute;
		bottom: -20px;
		left: 10%;
		width: 80%;
		height: 24px;
		background: linear-gradient(
			to bottom,
			rgba(255, 255, 255, 0.05),
			rgba(255, 255, 255, 0.01)
		);
		border-radius: 0 0 8px 8px;
		opacity: 0;
		transition: opacity 0.4s ease, height 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
	}

	.character-slot.hovered .stone-front,
	.character-slot.selected .stone-front {
		opacity: 1;
		height: 40px;
	}

	.stone-glow {
		position: absolute;
		inset: -15px;
		background: radial-gradient(ellipse at center, var(--char-color), transparent 70%);
		opacity: 0.15;
		border-radius: 50%;
		transition: opacity 0.4s ease;
	}

	.character-slot.hovered .stone-glow,
	.character-slot.selected .stone-glow {
		opacity: 0.5;
	}

	/* Name plate */
	.name-plate {
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-top: 0.5rem;
		padding: clamp(0.3rem, 0.4vw, 0.5rem) clamp(0.6rem, 1vw, 1.5rem);
		background: rgba(0, 0, 0, 0.5);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 6px;
		backdrop-filter: blur(10px);
		transition: all 0.4s ease;
		white-space: nowrap;
	}

	.character-slot.hovered .name-plate,
	.character-slot.selected .name-plate {
		background: rgba(0, 0, 0, 0.7);
		border-color: var(--char-color);
		box-shadow: 0 0 20px color-mix(in srgb, var(--char-color) 30%, transparent);
	}

	.name {
		font-family: 'Press Start 2P', 'Courier New', monospace;
		font-size: clamp(0.55rem, 1vw, 1rem);
		font-weight: bold;
		color: white;
		text-transform: uppercase;
		letter-spacing: 1px;
	}

	.character-slot.hovered .name,
	.character-slot.selected .name {
		color: var(--char-color);
		text-shadow: 0 0 10px var(--char-color);
	}

	.subtitle {
		font-size: clamp(0.4rem, 0.7vw, 0.65rem);
		color: rgba(255, 255, 255, 0.5);
		margin-top: 0.15rem;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		transition: color 0.3s ease;
	}

	.character-slot.hovered .subtitle,
	.character-slot.selected .subtitle {
		color: rgba(255, 255, 255, 0.8);
	}

	/* Particles */
	.particles {
		position: absolute;
		bottom: 15%;
		left: 50%;
		transform: translateX(-50%);
		width: clamp(110px, 12vw, 180px);
		height: clamp(190px, 20vw, 320px);
		pointer-events: none;
	}

	.particles.back {
		z-index: 0;
	}

	.particles.front {
		z-index: 3;
	}

	.particle {
		position: absolute;
		bottom: calc(var(--y) * 1%);
		left: calc(var(--x) * 1%);
		width: var(--size);
		height: var(--size);
		background: var(--char-color);
		border-radius: 50%;
		opacity: 0;
		box-shadow: 0 0 6px var(--char-color), 0 0 12px var(--char-color);
		transition: none;
	}

	.character-slot.hovered .particle,
	.character-slot.selected .particle {
		animation: particle-rise 1.4s ease-out var(--delay) infinite;
	}

	@keyframes particle-rise {
		0% {
			opacity: 0;
			transform: translateY(0) translateX(0) scale(0.5);
		}
		12% {
			opacity: 0.9;
			transform: translateY(-10px) translateX(calc(sin(var(--i) * 1rad) * 8px)) scale(1);
		}
		65% {
			opacity: 0.5;
		}
		100% {
			opacity: 0;
			transform: translateY(-60px) translateX(calc(sin(var(--i) * 2.5rad) * 15px)) scale(0.2);
		}
	}

	/* Spotlight — top and bottom glow */
	.spotlight {
		position: absolute;
		left: 50%;
		transform: translateX(-50%);
		width: 120%;
		height: 80%;
		opacity: 0;
		transition: opacity 0.4s ease;
		pointer-events: none;
		z-index: -1;
		top: -10%;
		background: radial-gradient(
			ellipse at 50% 0%,
			color-mix(in srgb, var(--char-color) 15%, transparent),
			transparent 60%
		);
	}

	.spotlight::after {
		content: '';
		position: absolute;
		bottom: -80%;
		left: 0;
		width: 100%;
		height: 100%;
		background: radial-gradient(
			ellipse at 50% 100%,
			color-mix(in srgb, var(--char-color) 15%, transparent),
			transparent 60%
		);
	}

	.character-slot.hovered .spotlight,
	.character-slot.selected .spotlight {
		opacity: 1;
	}
</style>
