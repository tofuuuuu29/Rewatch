<script setup lang="ts">
import {computed, ref, watch} from 'vue'
import {posterBackground} from '@/utils/poster.ts'
import type {MediaKey} from '@/types/index.ts'

const props = defineProps<{
	title: string
	category?: MediaKey
	label?: string // small caption above the title, e.g. "Anime"
	poster?: string // picture of the title; the coloured card is used when there is none
}>()

const background = computed(() => posterBackground(props.title, props.category))
const initial = computed(() => (props.title.trim()[0] ?? '?').toUpperCase())

// if the picture cannot be loaded, fall back to the coloured card
const failed = ref(false)
watch(() => props.poster, () => (failed.value = false))
const showPicture = computed(() => !!props.poster && !failed.value)
</script>

<template>
	<article class="poster" :style="{background}">
		<img v-if="showPicture" :src="poster" alt="" class="poster__img" loading="lazy" decoding="async"
			 referrerpolicy="no-referrer" @error="failed = true" />
		<span v-else class="poster__initial" aria-hidden="true">{{ initial }}</span>

		<div class="absolute left-3 right-3 top-3 flex items-start justify-between gap-2">
			<slot name="top" />
		</div>

		<div class="p-4 pt-10">
			<p v-if="label" class="text-[10px] font-semibold uppercase tracking-[.18em] text-white/60">{{ label }}</p>
			<h3 class="display mt-1 line-clamp-3 text-lg font-semibold leading-tight sm:text-xl">{{ title }}</h3>
			<slot name="meta" />
			<div class="mt-3 flex flex-wrap items-center gap-2">
				<slot name="actions" />
			</div>
		</div>
	</article>
</template>
