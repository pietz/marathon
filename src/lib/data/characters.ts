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
		age: '??',
		color: '#f1c40f',
		accentColor: '#d4ac0f',
		stats: [
			{ label: 'Tempo', value: 58, display: '58' },
			{ label: 'Ausdauer', value: 78, display: '78' },
			{ label: 'Kampfgeist', value: 97, display: '97' },
			{ label: 'Erfahrung', value: 10, display: '10' },
			{ label: 'Hilfeleistung', value: 65, display: '65' }
		],
		quote: '"Aufgeben können die anderen."',
		funFacts: [
			'Sieht nicht aus wie ein Sportler. Ist einer.',
			'Willenskraft: nicht messbar',
			'Hat mehr dumme Ideen als Trainingseinheiten',
			'Alkoholtoleranz und Laufleistung korrelieren bei ihm positiv'
		],
		imageFront: `${base}/images/tobi.png`,
		imageBack: null
	},
	{
		id: 'kevin',
		name: 'Kevin',
		subtitle: 'Mr. Punktspiel',
		age: '??',
		color: '#3498db',
		accentColor: '#2980b9',
		stats: [
			{ label: 'Tempo', value: 62, display: '62' },
			{ label: 'Ausdauer', value: 65, display: '65' },
			{ label: 'Kampfgeist', value: 70, display: '70' },
			{ label: 'Erfahrung', value: 5, display: '5' },
			{ label: 'Hilfeleistung', value: 3, display: '3' }
		],
		quote: '"Kann leider nicht – hab Punktspiel."',
		funFacts: [
			'Jeder Umzug fällt auf sein Punktspiel. Jedes. Einzelne. Mal.',
			'Hat mehr Punktspiele als die Bundesliga Spieltage hat',
			'Eigentlich fit. Nur halt nie da, wenn man ihn braucht.',
			'Sein Tennisschläger hat mehr Einsätze als sein Umzugskarton'
		],
		imageFront: `${base}/images/kevin.png`,
		imageBack: null
	},
	{
		id: 'jonas',
		name: 'Jonas',
		subtitle: 'Der Nette Doktor',
		age: '??',
		color: '#e74c3c',
		accentColor: '#c0392b',
		stats: [
			{ label: 'Tempo', value: 65, display: '65' },
			{ label: 'Ausdauer', value: 72, display: '72' },
			{ label: 'Kampfgeist', value: 62, display: '62' },
			{ label: 'Erfahrung', value: 15, display: '15' },
			{ label: 'Hilfeleistung', value: 90, display: '90' }
		],
		quote: '"Als Arzt würde ich davon abraten."',
		funFacts: [
			'So nett, dass man nichts gegen ihn sagen kann. Fast.',
			'Frisch geschieden – läuft jetzt buchstäblich vor seinen Problemen davon',
			'Diagnostiziert nach dem Zieleinlauf alle Verletzungen',
			'Der Einzige, der versteht, was ein Marathon dem Körper antut'
		],
		imageFront: `${base}/images/jonas.png`,
		imageBack: null
	},
	{
		id: 'alex',
		name: 'Alex',
		subtitle: 'Der Veteran',
		age: '45*',
		color: '#2ecc71',
		accentColor: '#27ae60',
		stats: [
			{ label: 'Tempo', value: 60, display: '60' },
			{ label: 'Ausdauer', value: 68, display: '68' },
			{ label: 'Kampfgeist', value: 88, display: '88' },
			{ label: 'Erfahrung', value: 95, display: '95' },
			{ label: 'Hilfeleistung', value: 75, display: '75' }
		],
		quote: '"Zu meiner Zeit ging der Marathon bergauf. In beide Richtungen."',
		funFacts: [
			'Offiziell 38. Laut Gruppe 45. Gefühlt 60.',
			'Glaubt, er hätte alle in Form gebracht. Jeder ging seinen eigenen Weg.',
			'Puls steigt gelegentlich auch ohne körperliche Anstrengung',
			'Der EINZIGE, der tatsächlich schon einen Marathon gelaufen ist'
		],
		imageFront: `${base}/images/alex.png`,
		imageBack: null
	}
];
