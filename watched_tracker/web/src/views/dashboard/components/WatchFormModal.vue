<script setup lang="ts">
import {ref} from 'vue'
import {site} from '@/config/site.ts'
import type {WatchEntry, WatchPayload, WatchStatus} from '@/types/index.ts'

const props = defineProps<{
	title: string
	entry: WatchEntry | null // null = adding a new title to the list
	saving: boolean
	error: string
}>()

const emit = defineEmits<{
	save: [payload: WatchPayload]
	close: []
}>()

const status = ref<WatchStatus>(props.entry?.status ?? 'plan_to_watch')
// a number input gives back a number, or an empty string when it is blank
const rating = ref<number | string>(props.entry?.rating ?? '')
const season = ref<number | string>(props.entry?.season ?? '')
const episode = ref<number | string>(props.entry?.episode ?? '')
const dateStarted = ref(props.entry?.date_started ?? '')

const toNumber = (value: number | string) => {
	if (String(value).trim() === '') return null
	const n = Number(value)
	return Number.isNaN(n) ? null : n
}

const submit = () => {
	emit('save', {
		status: status.value,
		rating: toNumber(rating.value),
		season: toNumber(season.value),
		episode: toNumber(episode.value),
		// the form no longer shows these two; an existing entry keeps whatever it already had
		notes: props.entry?.notes ?? '',
		date_started: dateStarted.value || null,
		date_finished: props.entry?.date_finished ?? null
	})
}

const input = 'field'
const label = 'field-label'
</script>

<template>
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-3 sm:p-4 md:bg-black/70 md:backdrop-blur-md"
		 @click.self="emit('close')">
		<div class="modal-panel max-h-[90dvh] w-full max-w-md overflow-y-auto overscroll-contain panel !bg-panel p-5 shadow-2xl sm:p-7">
			<div class="flex items-start justify-between gap-4">
				<div class="min-w-0">
					<p class="eyebrow">{{ entry ? 'Edit entry' : 'Add to my list' }}</p>
					<h3 class="mt-1 display break-words text-2xl font-semibold">{{ title }}</h3>
				</div>
				<button type="button" @click="emit('close')" aria-label="Close"
						class="-mr-2 -mt-2 flex h-10 w-10 shrink-0 items-center justify-center text-2xl leading-none text-white/60 transition hover:text-white">
					&times;
				</button>
			</div>

			<form class="mt-5 space-y-4" @submit.prevent="submit">
				<div>
					<label :class="label" for="status">Status</label>
					<select id="status" v-model="status" :class="input">
						<option v-for="s in site.statuses" :key="s.key" :value="s.key" class="bg-ink">{{ s.label }}</option>
					</select>
				</div>

				<div class="grid grid-cols-3 gap-3">
					<div>
						<label :class="label" for="rating">Rating</label>
						<input id="rating" v-model="rating" type="number" inputmode="numeric" min="1" max="10" placeholder="1-10" :class="input" />
					</div>
					<div>
						<label :class="label" for="season">Season</label>
						<input id="season" v-model="season" type="number" inputmode="numeric" min="1" :class="input" />
					</div>
					<div>
						<label :class="label" for="episode">Episode</label>
						<input id="episode" v-model="episode" type="number" inputmode="numeric" min="1" :class="input" />
					</div>
				</div>

				<div>
					<label :class="label" for="started">Started</label>
					<input id="started" v-model="dateStarted" type="date" :class="input" />
				</div>

				<p v-if="error" class="alert-error">{{ error }}</p>

				<div class="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
					<button type="button" @click="emit('close')" class="btn-ghost w-full sm:w-auto">
						Cancel
					</button>
					<button type="submit" :disabled="saving" class="btn-primary w-full sm:w-auto">
						{{ saving ? 'Saving...' : entry ? 'Save changes' : 'Add to list' }}
					</button>
				</div>
			</form>
		</div>
	</div>
</template>