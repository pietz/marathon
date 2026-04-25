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

	/** Create AudioContext on user gesture, decode buffers in background */
	init() {
		if (this.initialized) return;
		this.initialized = true;

		this.context = new AudioContext();
		const ctx = this.context;

		if (ctx.state === 'suspended') {
			ctx.resume();
		}

		// Decode pre-fetched buffers in background — each becomes playable as it resolves
		if (this.rawHover) {
			const raw = this.rawHover;
			this.rawHover = null;
			ctx.decodeAudioData(raw).then((buf) => { this.hoverBuffer = buf; }).catch(() => {});
		}

		this.rawSelect.forEach((raw, i) => {
			if (raw) {
				this.rawSelect[i] = null;
				ctx.decodeAudioData(raw).then((buf) => { this.selectBuffers[i] = buf; }).catch(() => {});
			}
		});
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
