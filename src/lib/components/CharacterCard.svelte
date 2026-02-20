<script lang="ts">
	import type { Character } from '$lib/data/characters';

	let {
		character,
		onClose
	}: {
		character: Character;
		onClose: () => void;
	} = $props();

	let visible = $state(false);

	$effect(() => {
		// Trigger entrance animation on next frame
		requestAnimationFrame(() => {
			visible = true;
		});
	});

	function handleClose() {
		visible = false;
		setTimeout(onClose, 300);
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			handleClose();
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			handleClose();
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
<div class="backdrop" class:visible onclick={handleBackdropClick}>
	<div
		class="card"
		class:visible
		style="--char-color: {character.color}; --char-accent: {character.accentColor};"
		role="dialog"
		aria-label="{character.name} character card"
	>
		<!-- Header -->
		<div class="card-header">
			<div class="header-info">
				<h2 class="card-name">{character.name}</h2>
				<p class="card-subtitle">{character.subtitle}</p>
			</div>
			<div class="card-age">
				<span class="age-number">{character.age}</span>
				<span class="age-label">ALTER</span>
			</div>
			<button class="close-btn" onclick={handleClose} aria-label="Close">✕</button>
		</div>

		<!-- Stats -->
		<div class="stats-section">
			<h3 class="section-title">STATS</h3>
			<div class="stats-grid">
				{#each character.stats as stat}
					<div class="stat-row">
						<span class="stat-label">{stat.label}</span>
						<div class="stat-bar-bg">
							<div
								class="stat-bar-fill"
								style="width: {visible ? stat.value : 0}%;"
							></div>
						</div>
						<span class="stat-value">{stat.display}</span>
					</div>
				{/each}
			</div>
		</div>

		<!-- Quote -->
		<div class="quote-section">
			<p class="quote">{character.quote}</p>
		</div>

		<!-- Fun Facts -->
		<div class="facts-section">
			<h3 class="section-title">INTEL</h3>
			<ul class="facts-list">
				{#each character.funFacts as fact}
					<li class="fact">{fact}</li>
				{/each}
			</ul>
		</div>
	</div>
</div>

<style>
	.backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
		transition: background 0.3s ease;
		padding: 2rem;
	}

	.backdrop.visible {
		background: rgba(0, 0, 0, 0.7);
		backdrop-filter: blur(5px);
	}

	.card {
		background: linear-gradient(
			135deg,
			rgba(20, 20, 35, 0.95),
			rgba(30, 30, 50, 0.95)
		);
		border: 1px solid var(--char-color);
		border-radius: 16px;
		padding: 2rem;
		max-width: 540px;
		width: 100%;
		max-height: 85vh;
		overflow-y: auto;
		box-shadow:
			0 0 30px color-mix(in srgb, var(--char-color) 20%, transparent),
			0 20px 60px rgba(0, 0, 0, 0.5);
		transform: scale(0.8) translateY(20px);
		opacity: 0;
		transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
	}

	.card.visible {
		transform: scale(1) translateY(0);
		opacity: 1;
	}

	/* Header */
	.card-header {
		display: flex;
		align-items: flex-start;
		gap: 1rem;
		margin-bottom: 0.5rem;
	}

	.header-info {
		flex: 1;
	}

	.card-name {
		font-family: 'Press Start 2P', 'Courier New', monospace;
		font-size: 1.5rem;
		color: var(--char-color);
		text-shadow: 0 0 20px var(--char-color);
		margin: 0;
		text-transform: uppercase;
	}

	.card-subtitle {
		color: rgba(255, 255, 255, 0.6);
		font-size: 0.85rem;
		margin: 0.25rem 0 0 0;
		text-transform: uppercase;
		letter-spacing: 1px;
	}

	.card-age {
		display: flex;
		flex-direction: column;
		align-items: center;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 8px;
		padding: 0.5rem 0.75rem;
	}

	.age-number {
		font-family: 'Press Start 2P', 'Courier New', monospace;
		font-size: 1.25rem;
		color: white;
		font-weight: bold;
	}

	.age-label {
		font-size: 0.6rem;
		color: rgba(255, 255, 255, 0.4);
		text-transform: uppercase;
		letter-spacing: 2px;
	}

	.age-disclaimer {
		font-size: 0.7rem;
		color: rgba(255, 255, 255, 0.35);
		font-style: italic;
		margin: 0 0 0.5rem 0;
	}

	.close-btn {
		background: rgba(255, 255, 255, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.2);
		color: rgba(255, 255, 255, 0.6);
		width: 32px;
		height: 32px;
		border-radius: 50%;
		cursor: pointer;
		font-size: 0.9rem;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s ease;
		flex-shrink: 0;
	}

	.close-btn:hover {
		background: rgba(255, 255, 255, 0.2);
		color: white;
	}

	/* Stats */
	.section-title {
		font-family: 'Press Start 2P', 'Courier New', monospace;
		font-size: 0.65rem;
		color: rgba(255, 255, 255, 0.4);
		letter-spacing: 3px;
		margin: 1.25rem 0 0.75rem 0;
	}

	.stats-grid {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.stat-row {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.stat-label {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.7);
		width: 120px;
		flex-shrink: 0;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.stat-bar-bg {
		flex: 1;
		max-width: 55%;
		height: 8px;
		background: rgba(255, 255, 255, 0.08);
		border-radius: 4px;
		overflow: hidden;
	}

	.stat-bar-fill {
		height: 100%;
		background: linear-gradient(90deg, var(--char-color), var(--char-accent));
		border-radius: 4px;
		transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
		box-shadow: 0 0 8px color-mix(in srgb, var(--char-color) 50%, transparent);
	}

	.stat-value {
		font-family: 'Press Start 2P', 'Courier New', monospace;
		font-size: 0.7rem;
		color: var(--char-color);
		width: 28px;
		text-align: right;
		flex-shrink: 0;
	}

	/* Quote */
	.quote-section {
		margin-top: 1.25rem;
		padding: 1rem;
		background: rgba(255, 255, 255, 0.03);
		border-left: 3px solid var(--char-color);
		border-radius: 0 8px 8px 0;
	}

	.quote {
		color: rgba(255, 255, 255, 0.7);
		font-style: italic;
		font-size: 0.9rem;
		margin: 0;
		line-height: 1.5;
	}

	/* Fun Facts */
	.facts-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}

	.fact {
		font-size: 0.8rem;
		color: rgba(255, 255, 255, 0.6);
		padding-left: 1rem;
		position: relative;
		line-height: 1.4;
	}

	.fact::before {
		content: '▸';
		position: absolute;
		left: 0;
		color: var(--char-color);
	}
</style>
