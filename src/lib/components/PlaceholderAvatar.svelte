<script lang="ts">
	let { color = '#888', name = '' }: { color?: string; name?: string } = $props();
</script>

<!-- Placeholder silhouette SVG for characters before real photos are added -->
<svg viewBox="0 0 200 400" xmlns="http://www.w3.org/2000/svg" class="placeholder-avatar">
	<!-- Body silhouette -->
	<defs>
		<linearGradient id="grad-{name}" x1="0%" y1="0%" x2="0%" y2="100%">
			<stop offset="0%" style="stop-color:{color};stop-opacity:0.9" />
			<stop offset="100%" style="stop-color:{color};stop-opacity:0.6" />
		</linearGradient>
	</defs>

	<!-- Head -->
	<ellipse cx="100" cy="60" rx="35" ry="40" fill="url(#grad-{name})" />

	<!-- Neck -->
	<rect x="88" y="95" width="24" height="20" rx="4" fill="url(#grad-{name})" />

	<!-- Torso -->
	<path d="M55 115 L145 115 L140 230 L60 230 Z" rx="10" fill="url(#grad-{name})" />

	<!-- Left arm -->
	<path d="M55 120 L25 200 L35 205 L70 145" fill="url(#grad-{name})" />

	<!-- Right arm -->
	<path d="M145 120 L175 200 L165 205 L130 145" fill="url(#grad-{name})" />

	<!-- Left leg -->
	<path d="M65 228 L55 370 L80 370 L95 228" fill="url(#grad-{name})" />

	<!-- Right leg -->
	<path d="M105 228 L120 370 L145 370 L135 228" fill="url(#grad-{name})" />

	<!-- Running shoe details -->
	<ellipse cx="62" cy="378" rx="22" ry="10" fill="url(#grad-{name})" opacity="0.8" />
	<ellipse cx="138" cy="378" rx="22" ry="10" fill="url(#grad-{name})" opacity="0.8" />

	<!-- Name initial on chest -->
	<text x="100" y="185" text-anchor="middle" font-size="36" font-weight="bold" fill="rgba(255,255,255,0.5)" font-family="sans-serif">
		{name.charAt(0)}
	</text>
</svg>

<style>
	.placeholder-avatar {
		width: 100%;
		height: 100%;
		filter: drop-shadow(0 0 10px rgba(0, 0, 0, 0.3));
	}
</style>
