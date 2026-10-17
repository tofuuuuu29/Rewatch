<script setup lang="ts">
import {useRouter} from 'vue-router'
import {site} from '@/config/site.ts'
import {useAuthStore} from '@/stores/auth.ts'

const auth = useAuthStore()
const router = useRouter()

const logout = () => {
	auth.logout()
	router.push({name: 'login'})
}
</script>

<template>
	<div class="min-h-screen">
		<header class="sticky top-0 z-40 border-b border-white/10 bg-ink/75 backdrop-blur-xl">
			<div class="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3.5 sm:px-6">
				<RouterLink :to="{name: 'dashboard'}" class="group flex items-center gap-2.5">
					<span class="flex h-9 w-9 items-center justify-center rounded-xl bg-accent text-accent-ink transition group-hover:rotate-6">
						<svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
							<rect x="3" y="4" width="18" height="16" rx="2.5" />
							<path d="M3 9h18M3 15h18M8 4v16M16 4v16" />
						</svg>
					</span>
					<span class="display text-xl font-semibold tracking-tight">{{ site.name }}</span>
				</RouterLink>

				<div class="flex items-center gap-3">
					<div v-if="auth.user" class="flex items-center gap-2.5">
						<span class="flex h-9 w-9 items-center justify-center rounded-full border border-white/15 bg-raised text-sm font-bold uppercase text-accent">
							{{ auth.user.username.slice(0, 1) }}
						</span>
						<div class="hidden text-left text-sm leading-tight sm:block">
							<p class="font-semibold">{{ auth.user.username }}</p>
							<p class="text-xs text-white/50">{{ auth.role?.name ?? 'No role' }}</p>
						</div>
					</div>
					<button type="button" @click="logout" class="btn-ghost !px-4 !py-2">Logout</button>
				</div>
			</div>
		</header>

		<main class="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-12">
			<slot />
		</main>

		<footer class="mx-auto max-w-6xl px-4 pb-10 text-xs leading-relaxed text-white/40 sm:px-6">
			<p>
				Movie, series and K-drama data and posters from TMDB. Anime data from MyAnimeList through Jikan.
				This product uses the TMDB API but is not endorsed or certified by TMDB.
			</p>
		</footer>
	</div>
</template>
