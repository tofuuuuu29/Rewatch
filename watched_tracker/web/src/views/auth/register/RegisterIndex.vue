<script setup lang="ts">
import AuthShell from '@/components/AuthShell.vue'
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {useAuthStore} from '@/stores/auth.ts'
import {errorMessage} from '@/utils/errors.ts'

const auth = useAuthStore()
const router = useRouter()

const form = ref({first_name: '', last_name: '', username: '', email: '', gender: '', password: ''})
const confirm = ref('')
const loading = ref(false)
const error = ref('')

const submit = async () => {
	error.value = ''
	if (form.value.password !== confirm.value) {
		error.value = 'Passwords do not match.'
		return
	}

	loading.value = true
	try {
		await auth.register({...form.value, username: form.value.username.trim()})
		router.push({name: 'login', query: {registered: '1'}})
	} catch (e) {
		error.value = errorMessage(e)
	} finally {
		loading.value = false
	}
}

const input = 'field'
const label = 'field-label'
</script>

<template>
	<AuthShell wide>
		<div>
			<h1 class="display mt-2 text-4xl font-semibold">Create account</h1>
			<p class="mt-2 text-sm text-white/60">Join to start tracking what you watch.</p>

			<form class="mt-8 space-y-5" @submit.prevent="submit">
				<div class="grid gap-4 sm:grid-cols-2">
					<div>
						<label :class="label" for="first_name">First name</label>
						<input id="first_name" v-model="form.first_name" required :class="input" />
					</div>
					<div>
						<label :class="label" for="last_name">Last name</label>
						<input id="last_name" v-model="form.last_name" required :class="input" />
					</div>
				</div>

				<div>
					<label :class="label" for="username">Username</label>
					<input id="username" v-model="form.username" required autocomplete="username" :class="input" />
				</div>

				<div>
					<label :class="label" for="email">Email</label>
					<input id="email" v-model="form.email" type="email" required autocomplete="email" :class="input" />
				</div>

				<div>
					<label :class="label" for="gender">Gender</label>
					<select id="gender" v-model="form.gender" :class="input">
						<option value="" class="bg-ink">Prefer not to say</option>
						<option value="Male" class="bg-ink">Male</option>
						<option value="Female" class="bg-ink">Female</option>
						<option value="Other" class="bg-ink">Other</option>
					</select>
				</div>

				<div class="grid gap-4 sm:grid-cols-2">
					<div>
						<label :class="label" for="password">Password</label>
						<input id="password" v-model="form.password" type="password" required minlength="6"
							   autocomplete="new-password" :class="input" />
					</div>
					<div>
						<label :class="label" for="confirm">Confirm password</label>
						<input id="confirm" v-model="confirm" type="password" required autocomplete="new-password" :class="input" />
					</div>
				</div>

				<p v-if="error" class="alert-error">{{ error }}</p>

				<button type="submit" :disabled="loading"
						class="btn-primary w-full">
					{{ loading ? 'Creating account...' : 'Register' }}
				</button>
			</form>

			<p class="mt-8 text-sm text-white/60">
				Already have an account?
				<RouterLink :to="{name: 'login'}" class="font-semibold text-accent hover:underline">Login</RouterLink>
			</p>
		</div>
	</AuthShell>
</template>
