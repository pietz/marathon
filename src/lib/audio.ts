// Audio manager for character selection sounds
// Preloads raw MP3 data on page load, decodes on first user gesture

import { base } from '$app/paths';

// Click sounds mapped to characters by index: Tobi, Kevin, Jonas, Alex
const selectSoundPaths = [
	`${base}/sounds/whoa.mp3`,
	`${base}/sounds/mamma-mia.mp3`,
	`${base}/sounds/yipee.mp3`,
	`${base}/sounds/yeahoo.mp3`
];
const hoverSoundPath = `${base}/sounds/coin.mp3`;

class AudioManager {
	private context: AudioContext | null = null;
	private hoverBuffer: AudioBuffer | null = null;
	private selectBuffers: (AudioBuffer | null)[] = [null, null, null, null];
	private initialized = false;

	// Raw ArrayBuffers fetched eagerly (no AudioContext needed)
	private rawHover: ArrayBuffer | null = null;
	private rawSelect: (ArrayBuffer | null)[] = [null, null, null, null];
	private preloaded = false;

	/** Fetch raw MP3 bytes on page load — no user gesture needed */
	preload() {
		if (this.preloaded) return;
		this.preloaded = true;

		fetch(hoverSoundPath)
			.then((r) => r.arrayBuffer())
			.then((buf) => { this.rawHover = buf; })
			.catch(() => {});

		selectSoundPaths.forEach((path, i) => {
			fetch(path)
				.then((r) => r.arrayBuffer())
				.then((buf) => { this.rawSelect[i] = buf; })
				.catch(() => {});
		});
	}

	/** Decode preloaded data — must be called from a user gesture */
	async init() {
		if (this.initialized) return;

		this.context = new AudioContext();
		const ctx = this.context;

		if (ctx.state === 'suspended') {
			await ctx.resume();
		}

		try {
			// Decode pre-fetched buffers (fast — no network wait)
			if (this.rawHover) {
				this.hoverBuffer = await ctx.decodeAudioData(this.rawHover);
				this.rawHover = null;
			}

			await Promise.all(
				this.rawSelect.map(async (raw, i) => {
					if (raw) {
						this.selectBuffers[i] = await ctx.decodeAudioData(raw);
						this.rawSelect[i] = null;
					}
				})
			);

			this.initialized = true;
		} catch (e) {
			console.warn('Audio init failed, will retry on next interaction', e);
			this.context = null;
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
