import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Home",
		component: () => import("@/pages/Home.vue"),
	},
	{
		name: "Login",
		path: "/login",
		component: () => import("@/pages/Login.vue"),
	},
	{
		name: "Dashboard",
		path: "/dashboard",
		component: () => import("@/components/Dashboard.vue"),
	},
	{
		name: "TestPage",
		path: "/test",
		component: () => import("@/views/TestPage.vue"),
	},
	{
		name: "ErpnextDashboard",
		path: "/erpnext-dashboard",
		component: () => import("@/views/ErpnextDashboard.vue"),
	},
]

const router = createRouter({
	history: createWebHistory(),
	routes,
})

router.beforeEach(async (to, from, next) => {
	const isLoggedIn = session.isAuthenticated()

	// Always allow access to login page
	if (to.name === "Login") {
		// If already logged in, redirect to dashboard
		if (isLoggedIn) {
			next({ name: "Dashboard" })
		} else {
			// Allow access to login page
			next()
		}
	} 
	// For protected pages, check authentication
	else if (to.name !== "Login" && !isLoggedIn) {
		next({ name: "Login" })
	} 
	// Otherwise, allow access
	else {
		next()
	}
})

export default router
