// Audio manager for character selection sounds
// Uses MP3 sound files for hover and select interactions

import { base } from '$app/paths';

// Click sounds mapped to characters by index: Tobi, Kevin, Jonas, Alex
const selectSounds = [
	`${base}/sounds/whoa.mp3`,
	`${base}/sounds/mamma-mia.mp3`,
	`${base}/sounds/yipee.mp3`,
	`${base}/sounds/yeahoo.mp3`
];

class AudioManager {
	private context: AudioContext | null = null;
	private hoverBuffer: AudioBuffer | null = null;
	private selectBuffers: (AudioBuffer | null)[] = [null, null, null, null];
	private initialized = false;

	/** Must be called from a user gesture (click/hover handler) */
	async init() {
		if (this.initialized) return;

		// Always create a fresh context during user gesture
		this.context = new AudioContext();
		const ctx = this.context;

		if (ctx.state === 'suspended') {
			await ctx.resume();
		}

		// Load all sounds in parallel
		try {
			const loads = [
				this.loadSound(ctx, `${base}/sounds/coin.mp3`).then((buf) => {
					this.hoverBuffer = buf;
				}),
				...selectSounds.map((path, i) =>
					this.loadSound(ctx, path).then((buf) => {
						this.selectBuffers[i] = buf;
					})
				)
			];
			await Promise.all(loads);
			this.initialized = true;
		} catch (e) {
			// Reset so next gesture can retry
			console.warn('Audio init failed, will retry on next interaction', e);
			this.context = null;
		}
	}

	private async loadSound(ctx: AudioContext, url: string): Promise<AudioBuffer | null> {
		try {
			const response = await fetch(url);
			const arrayBuffer = await response.arrayBuffer();
			return await ctx.decodeAudioData(arrayBuffer);
		} catch (e) {
			console.warn(`Failed to load sound: ${url}`, e);
			return null;
		}
	}

	private playBuffer(buffer: AudioBuffer | null) {
		if (!buffer || !this.context) return;
		const ctx = this.context;
		if (ctx.state === 'suspended') {
			ctx.resume();
		}
		const source = ctx.createBufferSource();
		source.buffer = buffer;
		source.connect(ctx.destination);
		source.start();
	}

	/** Play coin sound on character hover */
	playCharacterSound(_characterIndex: number) {
		this.playBuffer(this.hoverBuffer);
	}

	/** Play character-specific sound on select/click */
	playSelectSound(characterIndex: number) {
		this.playBuffer(this.selectBuffers[characterIndex] ?? null);
	}
}

export const audio = new AudioManager();
