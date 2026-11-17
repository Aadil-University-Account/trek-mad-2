import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// All /api calls are forwarded to the Flask server, so no CORS setup is needed.
export default defineConfig({
    plugins: [vue()],
    server: {
        port: 5173,
        proxy: {
            '/api': 'http://127.0.0.1:5000',
        },
    },
})