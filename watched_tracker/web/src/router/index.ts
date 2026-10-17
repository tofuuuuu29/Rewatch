import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '@/stores/auth.ts'
import {site} from '@/config/site.ts'

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{path: '/', redirect: {name: 'dashboard'}},
		{
			path: '/login',
			name: 'login',
			meta: {title: 'Login'},
			component: () => import('@/views/auth/login/LoginIndex.vue')
		},
		{
			path: '/register',
			name: 'register',
			meta: {title: 'Register'},
			component: () => import('@/views/auth/register/RegisterIndex.vue')
		},
		{
			path: '/dashboard',
			name: 'dashboard',
			meta: {requiresAuth: true, title: 'Dashboard'},
			component: () => import('@/views/dashboard/DashboardIndex.vue')
		},
		{path: '/:pathMatch(.*)*', redirect: {name: 'dashboard'}}
	],
	scrollBehavior: () => ({top: 0})
})

router.beforeEach(async (to) => {
	const auth = useAuthStore()
	auth.loadTokens()

	if (to.meta.requiresAuth && !auth.accessToken) {
		return {name: 'login'}
	}

	if ((to.name === 'login' || to.name === 'register') && auth.accessToken) {
		return {name: 'dashboard'}
	}

	// after a page refresh the token is still there but the user info is gone: load it again
	if (auth.accessToken && !auth.user) {
		try {
			await auth.loadProfile()
		} catch {
			// ignore: the API interceptor logs out when the token is invalid
		}
	}

	document.title = to.meta.title ? `${to.meta.title} | ${site.name}` : site.name
})

export default router
