<script setup lang="ts">
import {ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import AuthShell from '@/components/AuthShell.vue'
import {useAuthStore} from '@/stores/auth.ts'
import {errorMessage} from '@/utils/errors.ts'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const submit = async () => {
	error.value = ''
	loading.value = true
	try {
		await auth.login(username.value.trim(), password.value)
		router.push({name: 'dashboard'})
	} catch (e) {
		error.value = errorMessage(e)
	} finally {
		loading.value = false
	}
}
</script>

<template>
	<AuthShell>
		<h1 class="display mt-2 text-4xl font-semibold">Welcome back</h1>
		<p class="mt-2 text-sm text-white/60">Log in to see what you've watched.</p>

		<p v-if="route.query.registered" class="alert-ok mt-6">Account created. You can log in now.</p>

		<form class="mt-8 space-y-5" @submit.prevent="submit">
			<div>
				<label class="field-label" for="username">Username</label>
				<input id="username" v-model="username" required autocomplete="username" class="field" />
			</div>
			<div>
				<label class="field-label" for="password">Password</label>
				<input id="password" v-model="password" type="password" required autocomplete="current-password" class="field" />
			</div>

			<p v-if="error" class="alert-error">{{ error }}</p>

			<button type="submit" :disabled="loading" class="btn-primary w-full">
				{{ loading ? 'Logging in...' : 'Login' }}
			</button>
		</form>

		<p class="mt-8 text-sm text-white/60">
			No account yet?
			<RouterLink :to="{name: 'register'}" class="font-semibold text-accent hover:underline">Register</RouterLink>
		</p>
	</AuthShell>
</template>
