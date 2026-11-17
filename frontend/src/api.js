import axios from 'axios'
import { auth, logout } from './auth'

// One axios instance used by every component
const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
    if (auth.token) config.headers.Authorization = 'Bearer ' + auth.token
    return config
})

// token expired / account blacklisted -> go to login
api.interceptors.response.use(
    (res) => res,
    (err) => {
        const status = err.response && err.response.status
        if ((status === 401 || status === 422) && auth.token) {
            logout()
            window.location.href = '/login'
        }
        return Promise.reject(err)
    },
)

export function errorMessage(err) {
    return (err.response && err.response.data && err.response.data.message) || 'Something went wrong'
}

export default api