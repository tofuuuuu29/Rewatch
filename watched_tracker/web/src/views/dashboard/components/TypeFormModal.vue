<script setup lang="ts">
import {computed, ref, watch} from 'vue'
import {site} from '@/config/site.ts'
import {useMediaStore} from '@/stores/media.ts'
import {linkOf} from '@/utils/types.ts'
import type {MediaKey, TypePayload, TypeRow} from '@/types/index.ts'

const props = defineProps<{
	item: TypeRow | null // null = adding a new type
	saving: boolean
	error: string
}>()

const emit = defineEmits<{
	save: [payload: TypePayload]
	close: []
}>()

const media = useMediaStore()

const start = props.item ? linkOf(props.item) : null
const kind = ref<MediaKey>(start?.cfg.key ?? site.media[0].key)
const mediaId = ref<number | ''>(start?.mediaId ?? '')

const cfg = computed(() => site.media.find((m) => m.key === kind.value)!)
const titles = computed(() => media.items[kind.value])

// picking another media type clears the chosen title
watch(kind, () => (mediaId.value = ''))

const submit = () => {
	if (mediaId.value === '') return
	// the API needs exactly one media field set, so always send all four
	const payload: TypePayload = {anime: null, movie: null, tv_series: null, kdrama: null}
	payload[cfg.value.typeField as keyof TypePayload] = mediaId.value
	emit('save', payload)
}

const input = 'w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm outline-none transition focus:border-accent'
const label = 'mb-1.5 block text-xs uppercase tracking-widest text-white/50'
</script>

<template>
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-3 sm:p-4 md:bg-black/70 md:backdrop-blur-sm"
		 @click.self="emit('close')">
		<div class="modal-panel max-h-[90dvh] w-full max-w-md overflow-y-auto rounded-3xl border border-white/10 bg-ink p-5 sm:p-6">
			<div class="flex items-start justify-between gap-4">
				<h3 class="text-xl font-semibold">{{ item ? 'Edit' : 'Add' }} Type</h3>
				<button type="button" @click="emit('close')" aria-label="Close"
						class="-mr-2 -mt-2 flex h-10 w-10 items-center justify-center text-2xl leading-none text-white/60 transition hover:text-white">
					&times;
				</button>
			</div>

			<form class="mt-5 space-y-4" @submit.prevent="submit">
				<div>
					<label :class="label" for="kind">Media type</label>
					<select id="kind" v-model="kind" :class="input">
						<option v-for="m in site.media" :key="m.key" :value="m.key" class="bg-ink">{{ m.singular }}</option>
					</select>
				</div>

				<div>
					<label :class="label" for="title">Title</label>
					<select id="title" v-model="mediaId" required :class="input">
						<option value="" disabled class="bg-ink">Choose a title...</option>
						<option v-for="t in titles" :key="t.id" :value="t.id" class="bg-ink">{{ t[cfg.nameField] }}</option>
					</select>
					<p v-if="!titles.length" class="mt-2 text-xs text-white/50">
						No {{ cfg.label.toLowerCase() }} yet. Add one in its tab first.
					</p>
				</div>

				<p v-if="error" class="rounded-xl bg-red-500/10 px-4 py-3 text-sm text-red-300">{{ error }}</p>

				<div class="flex justify-end gap-3 pt-2">
					<button type="button" @click="emit('close')"
							class="rounded-full border border-white/15 px-5 py-2.5 text-sm transition hover:border-white/40">
						Cancel
					</button>
					<button type="submit" :disabled="saving || mediaId === ''"
							class="rounded-full bg-accent px-5 py-2.5 text-sm font-semibold text-white transition hover:brightness-110 disabled:opacity-60">
						{{ saving ? 'Saving...' : 'Save' }}
					</button>
				</div>
			</form>
		</div>
	</div>
</template>
