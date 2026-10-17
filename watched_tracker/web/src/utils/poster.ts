import type {MediaKey} from '@/types/index.ts'

// one base hue per category, so every tab has its own colour
export const CATEGORY_HUE: Record<MediaKey, number> = {
	movies: 38, // gold
	anime: 340, // pink
	kdrama: 268, // violet
	tvseries: 178 // teal
}

const hash = (text: string) => {
	let h = 0
	for (let i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) >>> 0
	return h
}

// a stable gradient for a title: the same title always gets the same poster
export const posterBackground = (title: string, category?: MediaKey) => {
	const base = category ? CATEGORY_HUE[category] : 220
	const h = (base + (hash(title) % 36) - 18 + 360) % 360
	return `linear-gradient(160deg, hsl(${h} 68% 42%) 0%, hsl(${(h + 28) % 360} 58% 22%) 55%, hsl(${(h + 50) % 360} 50% 10%) 100%)`
}

export const categoryColor = (category?: MediaKey) =>
	`hsl(${category ? CATEGORY_HUE[category] : 220} 85% 62%)`
