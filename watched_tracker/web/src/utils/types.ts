import {site} from '@/config/site.ts'
import type {MediaConfig, TypeRow} from '@/types/index.ts'

// which media type (and which title id) a Type row points to
export function linkOf(row: TypeRow): {cfg: MediaConfig; mediaId: number} | null {
	for (const cfg of site.media) {
		const id = row[cfg.typeField as keyof TypeRow]
		if (typeof id === 'number') return {cfg, mediaId: id}
	}
	return null
}
