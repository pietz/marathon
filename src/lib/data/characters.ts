import { base } from '$app/paths';

export interface CharacterStat {
	label: string;
	value: number; // 0-100
	display: string;
}

export interface Character {
	id: string;
	name: string;
	subtitle: string;
	age: string;
	color: string;
	accentColor: string;
	stats: CharacterStat[];
	quote: string;
	funFacts: string[];
	imageFront: string | null; // null = use placeholder
	imageBack: string | null;
}

// Unified stats across all characters:
// Tempo, Ausdauer, Kampfgeist, Erfahrung, Hilfeleistung

export const characters: Character[] = [
	{
		id: 'toby',
		name: 'Tobi',
		subtitle: 'Das Kampfschwein',
		age: '33',
		color: '#f1c40f',
		accentColor: '#d4ac0f',
		stats: [
			{ label: 'Tempo', value: 58, display: '58' },
			{ label: 'Ausdauer', value: 78, display: '78' },
			{ label: 'Kampfgeist', value: 97, display: '97' },
			{ label: 'Erfahrung', value: 71, display: '71' },
			{ label: 'Hilfeleistung', value: 64, display: '64' }
		],
		quote: '"Klingt nach einer richtig dummen Idee. Bin dabei."',
		funFacts: [
			'Nimmt auf eine einsame Insel mit: Alkohol und zwei schlechte Entscheidungen.',
			'Sieht nicht aus wie ein Sportler. Ist einer.',
			'Carbo-Loading heißt bei ihm: Weizenbier.',
			'Vereinsvorsitzender der Zauberflöten. Mitglieder: 3. Vereinszweck: fragwürdig.'
		],
		imageFront: `${base}/images/tobi.png`,
		imageBack: null
	},
	{
		id: 'kevin',
		name: 'Kevin',
		subtitle: 'Das Einzelkind',
		age: '34',
		color: '#3498db',
		accentColor: '#2980b9',
		stats: [
			{ label: 'Tempo', value: 81, display: '81' },
			{ label: 'Ausdauer', value: 65, display: '65' },
			{ label: 'Kampfgeist', value: 70, display: '70' },
			{ label: 'Erfahrung', value: 39, display: '39' },
			{ label: 'Hilfeleistung', value: 13, display: '13' }
		],
		quote: '"Kann leider nicht – hab Punktspiel."',
		funFacts: [
			'Auge-Hand-Koordination – Weltklasse.',
			'Auge-Umzugskarton-Koordination – nicht existent.',
			'Besitzt eine Bohrmaschine. Originalverpackt. Seit 2019.',
			'Findet immer jemanden, der für ihn anpackt – und nennt es Führungsqualität.'
		],
		imageFront: `${base}/images/kevin.png`,
		imageBack: null
	},
	{
		id: 'jonas',
		name: 'Jonas',
		subtitle: 'Der Nette Doktor',
		age: '34',
		color: '#e74c3c',
		accentColor: '#c0392b',
		stats: [
			{ label: 'Tempo', value: 65, display: '65' },
			{ label: 'Ausdauer', value: 72, display: '72' },
			{ label: 'Kampfgeist', value: 62, display: '62' },
			{ label: 'Erfahrung', value: 49, display: '49' },
			{ label: 'Hilfeleistung', value: 99, display: '99' }
		],
		quote: '"Als Arzt würde ich davon abraten."',
		funFacts: [
			'Keiner kann etwas Schlechtes über ihn sagen. Außer seine Ex-Frau.',
			'50 % aller WhatsApps an ihn starten mit: Kurze medizinische Frage.',
			'Entschuldigt sich beim Überholen.',
			'Kann nicht Nein sagen. Deshalb läuft er jetzt auch einen Marathon.'
		],
		imageFront: `${base}/images/jonas.png`,
		imageBack: null
	},
	{
		id: 'alex',
		name: 'Alex',
		subtitle: 'Der Ü40-Veteran',
		age: '45',
		color: '#2ecc71',
		accentColor: '#27ae60',
		stats: [
			{ label: 'Tempo', value: 77, display: '77' },
			{ label: 'Ausdauer', value: 68, display: '68' },
			{ label: 'Kampfgeist', value: 88, display: '88' },
			{ label: 'Erfahrung', value: 83, display: '83' },
			{ label: 'Hilfeleistung', value: 75, display: '75' }
		],
		quote: '"Zu meiner Zeit gab es Marathon nur in Athen."',
		funFacts: [
			'CrossFit, Hyrox, Marathon – alles, nur um nicht arbeiten zu müssen.',
			'Wenn der Run nicht auf Insta ist, hat er nicht stattgefunden.',
			'Puls steigt gelegentlich auch ohne körperliche Anstrengung.',
			'Teilt alles. Außer sein Essen. Da hört die Freundschaft auf.'
		],
		imageFront: `${base}/images/alex.png`,
		imageBack: null
	}
];
