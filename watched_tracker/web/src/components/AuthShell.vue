<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from 'vue'
import api from '@/axiosInstance.ts'
import {site} from '@/config/site.ts'
import {posterBackground} from '@/utils/poster.ts'
import type {MediaKey} from '@/types/index.ts'

defineProps<{wide?: boolean}>()

// decorative "posters": shown while the trending slides load, or if they can't load
const tiles: {t: string; c: MediaKey}[] = [
	{t: 'Midnight Run', c: 'movies'},
	{t: 'Kaiju Academy', c: 'anime'},
	{t: 'Seoul Nights', c: 'kdrama'},
	{t: 'The Long Season', c: 'tvseries'},
	{t: 'Paper Moon', c: 'movies'},
	{t: 'Starlit Duel', c: 'anime'}
]

// ---- trending slideshow (GET /api/discover/trending/, public) ----
interface Slide {
	title: string
	year: string
	category: string
	image_url: string
	source: string
}

const SLIDE_MS = 3000 // how long each slide stays
const FADE_MS = 1000 // how long the crossfade takes

const slides = ref<Slide[]>([])
const broken = ref<Set<string>>(new Set()) // images that failed to load
const fit = ref<Record<string, 'wide' | 'tall'>>({}) // measured when each image loads
const index = ref(0)
let timer: number | undefined

// the poster panel only exists from 1024px up
const desktop = window.matchMedia('(min-width: 1024px)')
let loaded = false

// people who asked their system for less motion keep the fade but not the zoom
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

// only slides whose image works
const shown = computed(() => slides.value.filter((s) => !broken.value.has(s.image_url)))
const current = computed(() => shown.value[index.value % Math.max(shown.value.length, 1)])
const isOn = (i: number) => i === index.value % Math.max(shown.value.length, 1)

// the new slide fades in on top while the old one stays fully visible underneath,
// then the old one disappears, so there is never a dark gap
const fadeStyle = (url: string, i: number) => {
	const on = isOn(i) && !!fit.value[url]
	return {
		opacity: on ? 1 : 0,
		zIndex: on ? 10 : 0,
		transition: `opacity ${on ? FADE_MS : 0}ms ease-in-out ${on ? 0 : FADE_MS}ms`,
		willChange: 'opacity'
	}
}

// slow zoom that keeps going while the slide fades out, so the motion never stops or jumps
const zoomStyle = (url: string, i: number) => {
	const on = isOn(i) && !!fit.value[url]
	return {
		transform: on && !reduceMotion ? 'scale(1.06)' : 'scale(1)',
		transition: reduceMotion ? 'none' : `transform ${on ? SLIDE_MS + FADE_MS : 0}ms linear ${on ? 0 : FADE_MS}ms`,
		willChange: 'transform'
	}
}

const stop = () => {
	window.clearInterval(timer)
	timer = undefined
}

const start = () => {
	stop()
	if (!desktop.matches || shown.value.length < 2 || document.hidden) return
	timer = window.setInterval(() => {
		index.value = (index.value + 1) % shown.value.length
	}, SLIDE_MS)
}

const go = (i: number) => {
	index.value = i
	start() // restart the countdown so it doesn't jump right after a click
}

const onImageError = (url: string) => {
	broken.value = new Set(broken.value).add(url)
	if (index.value >= shown.value.length) index.value = 0
}

// tall pictures (posters) are shown whole over a blurred copy; wide ones fill the panel
const onImageLoad = (url: string, e: Event) => {
	const img = e.target as HTMLImageElement
	const kind = img.naturalWidth / img.naturalHeight < 1.2 ? 'tall' : 'wide'
	fit.value = {...fit.value, [url]: kind}
}

// pause while the tab is hidden
const onVisibility = () => (document.hidden ? stop() : start())

// download the slides only once the panel is actually visible
const loadSlides = async () => {
	if (loaded || !desktop.matches) return
	loaded = true
	try {
		const {data} = await api.get<Slide[]>('/discover/trending/')
		slides.value = Array.isArray(data) ? data.filter((s) => s.title && s.image_url) : []
		start()
	} catch {
		loaded = false // keep the decorative posters, and try again if the screen changes
	}
}

// a tablet turned sideways, or a window made wider or narrower
const onScreenChange = () => {
	if (desktop.matches) {
		if (loaded) start()
		else loadSlides()
	} else {
		stop()
	}
}

onMounted(() => {
	document.addEventListener('visibilitychange', onVisibility)
	desktop.addEventListener('change', onScreenChange)
	loadSlides()
})

onBeforeUnmount(() => {
	stop()
	document.removeEventListener('visibilitychange', onVisibility)
	desktop.removeEventListener('change', onScreenChange)
})
</script>

<template>
	<div class="grid min-h-screen lg:grid-cols-[1.05fr_1fr]">
		<!-- left: brand + trending slideshow (from 1024px up) -->
		<aside class="relative hidden overflow-hidden border-r border-white/10 lg:block">
			<!-- fallback: tilted poster wall -->
			<div v-if="!shown.length" class="absolute inset-0 grid -rotate-6 scale-125 grid-cols-3 gap-4 p-10 opacity-60" aria-hidden="true">
				<div v-for="(tile, i) in tiles" :key="tile.t" class="poster !rounded-2xl"
					 :class="i % 2 ? 'translate-y-10' : '-translate-y-6'"
					 :style="{background: posterBackground(tile.t, tile.c)}">
					<span class="poster__initial">{{ tile.t[0] }}</span>
				</div>
			</div>

			<!-- trending slides: new one fades in on top, old one stays underneath until it's done -->
			<div v-else class="absolute inset-0 overflow-hidden" aria-hidden="true">
				<div v-for="(slide, i) in shown" :key="slide.image_url" class="absolute inset-0" :style="fadeStyle(slide.image_url, i)">
					<div class="absolute inset-0" :style="zoomStyle(slide.image_url, i)">
						<!-- tall poster: blurred copy fills the panel behind it -->
						<img v-if="fit[slide.image_url] === 'tall'" :src="slide.image_url" alt="" referrerpolicy="no-referrer" decoding="async"
							 class="absolute inset-0 h-full w-full scale-125 object-cover opacity-50 blur-xl" />
						<img :src="slide.image_url" alt="" referrerpolicy="no-referrer" decoding="async"
							 :class="fit[slide.image_url] === 'tall'
								? 'absolute inset-0 h-full w-full object-contain px-10 pb-60 pt-28 xl:pb-72'
								: 'absolute inset-0 h-full w-full object-cover'"
							 @load="onImageLoad(slide.image_url, $event)"
							 @error="onImageError(slide.image_url)" />
					</div>
				</div>
			</div>

			<div class="absolute inset-0 bg-gradient-to-t from-ink via-ink/50 to-ink/25"></div>

			<!-- what is on screen + dots -->
			<div v-if="shown.length && current" class="absolute inset-x-8 top-10 z-20 flex items-start justify-between gap-6 xl:inset-x-12">
				<div class="min-w-0">
					<p class="eyebrow">Trending now</p>
					<p class="mt-1 truncate text-sm text-white/80">
						{{ current.title }}<span v-if="current.year" class="text-white/50"> · {{ current.year }}</span>
					</p>
					<p class="text-xs text-white/50">{{ current.category }}</p>
				</div>
				<div v-if="shown.length > 1" class="flex shrink-0 items-center gap-2 pt-1">
					<button v-for="(slide, i) in shown" :key="slide.image_url" type="button"
							class="h-1.5 rounded-full transition-all"
							:class="isOn(i) ? 'w-6 bg-accent' : 'w-1.5 bg-white/30 hover:bg-white/60'"
							:aria-label="`Show ${slide.title}`" @click="go(i)"></button>
				</div>
			</div>

			<div class="relative z-20 flex h-full flex-col justify-end p-8 xl:p-12">
				<p class="eyebrow">{{ site.name }}</p>
				<h2 class="display mt-3 max-w-md text-4xl font-semibold leading-[1.05] xl:text-5xl">
					Every story you've <em class="text-accent">finished</em>, in one place.
				</h2>
				<p class="mt-4 max-w-sm text-white/60">Movies, anime, K-dramas and series. Rate them, track your episodes, never lose your place.</p>
				<p v-if="shown.length" class="mt-6 text-[11px] text-white/35">Trending data from TMDB and AniList. This product uses the TMDB API but is not endorsed or certified by TMDB.</p>
			</div>
		</aside>

		<!-- right: the form -->
		<div class="flex items-center justify-center px-4 py-10 sm:px-8">
			<div class="fade-up w-full" :class="wide ? 'max-w-lg' : 'max-w-md'">
				<p class="eyebrow lg:hidden">{{ site.name }}</p>
				<slot />
			</div>
		</div>
	</div>
</template>