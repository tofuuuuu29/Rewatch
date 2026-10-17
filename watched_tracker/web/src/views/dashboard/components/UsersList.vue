<script setup lang="ts">
import {computed, onMounted, ref} from 'vue'
import api from '@/axiosInstance.ts'
import {useAuthStore} from '@/stores/auth.ts'
import {errorMessage} from '@/utils/errors.ts'
import type {Role, User} from '@/types/index.ts'

const auth = useAuthStore()

const users = ref<User[]>([])
const roles = ref<Role[]>([])
const loading = ref(true)
const error = ref('')

const roleName = computed(() => {
	const map = new Map(roles.value.map((r) => [r.id, r.name]))
	return (id: number | null) => (id === null ? 'No role' : (map.get(id) ?? '-'))
})

onMounted(async () => {
	try {
		const [u, r] = await Promise.all([api.get<User[]>('/users/'), api.get<Role[]>('/roles/')])
		users.value = u.data
		roles.value = r.data
	} catch (e) {
		error.value = errorMessage(e)
	} finally {
		loading.value = false
	}
})

const remove = async (user: User) => {
	if (!window.confirm(`Delete user "${user.username}"?`)) return
	try {
		await api.delete(`/users/${user.id}/`)
		users.value = users.value.filter((u) => u.id !== user.id)
	} catch (e) {
		error.value = errorMessage(e)
	}
}
</script>

<template>
	<p v-if="error" class="mb-4 rounded-xl bg-red-500/10 px-4 py-3 text-sm text-red-300">{{ error }}</p>
	<p v-if="loading" class="py-12 text-center text-white/50">Loading...</p>

	<div v-else class="overflow-x-auto panel">
		<table class="w-full min-w-[560px] text-left text-sm">
			<thead class="border-b border-white/10 text-[11px] font-semibold uppercase tracking-[.16em] text-white/50">
				<tr>
					<th class="px-4 py-4 sm:px-6">Username</th>
					<th class="px-4 py-4">Name</th>
					<th class="px-4 py-4">Email</th>
					<th class="px-4 py-4">Role</th>
					<th class="px-4 py-4 text-right sm:px-6">Actions</th>
				</tr>
			</thead>
			<tbody>
				<tr v-for="u in users" :key="u.id" class="border-b border-white/5 last:border-0 hover:bg-white/[0.04]">
					<td class="px-4 py-4 font-medium sm:px-6">{{ u.username }}</td>
					<td class="px-4 py-4 text-white/70">{{ u.first_name }} {{ u.last_name }}</td>
					<td class="px-4 py-4 text-white/70">{{ u.email || '-' }}</td>
					<td class="px-4 py-4">
						<span class="rounded-full bg-accent/15 px-3 py-1 text-xs font-semibold text-accent">{{ roleName(u.role) }}</span>
					</td>
					<td class="px-4 py-4 text-right sm:px-6">
						<button v-if="u.id !== auth.user?.id" type="button" @click="remove(u)"
								class="btn-chip-danger">
							Delete
						</button>
						<span v-else class="text-xs text-white/40">You</span>
					</td>
				</tr>
			</tbody>
		</table>
	</div>
</template>
