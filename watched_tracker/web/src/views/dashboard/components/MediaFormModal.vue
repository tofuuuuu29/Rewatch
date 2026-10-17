<script setup lang="ts">
import {ref} from 'vue'
import type {MediaConfig, MediaItem} from '@/types/index.ts'

const props = defineProps<{
	cfg: MediaConfig
	item: MediaItem | null // null = adding a new title
	initialName?: string // pre-fills the title when adding
	saving: boolean
	error: string
}>()

const emit = defineEmits<{
	save: [payload: Partial<MediaItem>]
	close: []
}>()

const name = ref(String(props.item?.[props.cfg.nameField] ?? props.initialName ?? ''))
const season = ref(props.item?.season != null ? String(props.item.season) : '')
const episode = ref(props.item?.episode != null ? String(props.item.episode) : '')

const toNumber = (value: string) => (value.trim() === '' ? null : Number(value))

const submit = () => {
	const payload: Partial<MediaItem> = {[props.cfg.nameField]: name.value.trim()}
	if (props.cfg.hasProgress) {
		payload.season = toNumber(season.value)
		payload.episode = toNumber(episode.value)
	}
	emit('save', payload)
}

const input = 'field'
const label = 'field-label'
</script>

<template>
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-3 sm:p-4 md:bg-black/70 md:backdrop-blur-md"
		 @click.self="emit('close')">
		<div class="modal-panel max-h-[90dvh] w-full max-w-md overflow-y-auto panel !bg-panel p-5 shadow-2xl sm:p-7">
			<div class="flex items-start justify-between gap-4">
				<h3 class="display text-2xl font-semibold">{{ item ? 'Edit' : 'Add' }} {{ cfg.singular }}</h3>
				<button type="button" @click="emit('close')" aria-label="Close"
						class="-mr-2 -mt-2 flex h-10 w-10 items-center justify-center text-2xl leading-none text-white/60 transition hover:text-white">
					&times;
				</button>
			</div>

			<form class="mt-5 space-y-4" @submit.prevent="submit">
				<div>
					<label :class="label" for="title">Title</label>
					<input id="title" v-model="name" required maxlength="255" :class="input" />
				</div>

				<div v-if="cfg.hasProgress" class="grid grid-cols-2 gap-4">
					<div>
						<label :class="label" for="season">Season</label>
						<input id="season" v-model="season" type="number" min="1" :class="input" />
					</div>
					<div>
						<label :class="label" for="episode">Episode</label>
						<input id="episode" v-model="episode" type="number" min="1" :class="input" />
					</div>
				</div>

				<p v-if="error" class="alert-error">{{ error }}</p>

				<div class="flex justify-end gap-3 pt-2">
					<button type="button" @click="emit('close')"
							class="btn-ghost">
						Cancel
					</button>
					<button type="submit" :disabled="saving"
							class="btn-primary">
						{{ saving ? 'Saving...' : 'Save' }}
					</button>
				</div>
			</form>
		</div>
	</div>
</template>
