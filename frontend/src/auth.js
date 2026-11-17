import { reactive } from 'vue'

// Small shared login state (kept in localStorage so refresh does not log out)
export const auth = reactive({
    token: localStorage.getItem('token'),
    role: localStorage.getItem('role'),
    name: localStorage.getItem('name'),
})

export function saveLogin(data) {
    auth.token = data.token
    auth.role = data.role
    auth.name = data.name
    localStorage.setItem('token', data.token)
    localStorage.setItem('role', data.role)
    localStorage.setItem('name', data.name)
}

export function logout() {
    auth.token = auth.role = auth.name = null
    localStorage.clear()
}