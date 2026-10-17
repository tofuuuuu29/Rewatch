<script setup lang="ts">
import {useMediaStore} from '@/stores/media.ts'
import {linkOf} from '@/utils/types.ts'
import type {TypeRow} from '@/types/index.ts'

defineProps<{
	items: TypeRow[]
	loading: boolean
}>()

defineEmits<{
	edit: [row: TypeRow]
	remove: [row: TypeRow]
}>()

const media = useMediaStore()

// the type label and the title name for one row
const describe = (row: TypeRow) => {
	const link = linkOf(row)
	if (!link) return {type: '-', title: '-'}
	const found = media.items[link.cfg.key].find((m) => m.id === link.mediaId)
	return {type: link.cfg.singular, title: String(found?.[link.cfg.nameField] ?? `#${link.mediaId}`)}
}
</script>

<template>
	<p v-if="loading" class="py-12 text-center text-white/50">Loading...</p>
	<p v-else-if="!items.length" class="py-12 text-center text-white/50">
		No types yet.
	</p>

	<div v-else class="overflow-x-auto rounded-3xl border border-white/10 bg-white/[0.03]">
		<table class="w-full min-w-[420px] text-left text-sm">
			<thead class="border-b border-white/10 text-xs uppercase tracking-widest text-white/50">
				<tr>
					<th class="px-4 py-4 sm:px-6">Type</th>
					<th class="px-4 py-4">Title</th>
					<th class="px-4 py-4 text-right sm:px-6">Actions</th>
				</tr>
			</thead>
			<tbody>
				<tr v-for="row in items" :key="row.id"
					class="border-b border-white/5 transition last:border-0 hover:bg-white/[0.04]">
					<td class="px-4 py-4 sm:px-6">
						<span class="rounded-full bg-white/10 px-3 py-1 text-xs">{{ describe(row).type }}</span>
					</td>
					<td class="px-4 py-4 font-medium">{{ describe(row).title }}</td>
					<td class="whitespace-nowrap px-4 py-4 text-right sm:px-6">
						<button type="button" @click="$emit('edit', row)"
								class="rounded-full bg-white/10 px-3 py-1.5 text-xs transition hover:bg-accent">
							Edit
						</button>
						<button type="button" @click="$emit('remove', row)"
								class="ml-2 rounded-full bg-white/10 px-3 py-1.5 text-xs transition hover:bg-red-500">
							Delete
						</button>
					</td>
				</tr>
			</tbody>
		</table>
	</div>
</template>
