import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '../auth'
import LandingView from '../components/LandingView.vue'
import LoginView from '../components/LoginView.vue'
import RegisterView from '../components/RegisterView.vue'
import AdminView from '../views/AdminView.vue'
import StaffView from '../views/StaffView.vue'
import UserView from '../views/UserView.vue'

const routes = [
    { path: '/', component: LandingView },
    { path: '/login', component: LoginView },
    { path: '/register', component: RegisterView },
    { path: '/admin', component: AdminView, meta: { role: 'admin' } },
    { path: '/staff', component: StaffView, meta: { role: 'staff' } },
    { path: '/user', component: UserView, meta: { role: 'user' } },
    { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({ history: createWebHistory(), routes })

// Role based route protection
router.beforeEach((to) => {
    if (to.meta.role) {
        if (!auth.token) return '/login'
        if (auth.role !== to.meta.role) return '/' + auth.role
    }
    // already logged in people do not need login/register page
    if ((to.path === '/login' || to.path === '/register') && auth.token) {
        return '/' + auth.role
    }
})

export default router