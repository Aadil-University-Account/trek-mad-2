<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { errorMessage } from '../api'

const treks = ref([])
const locations = ref([])
const myBookings = ref([])
const message = ref('')
const error = ref('')

const filters = ref({ q: '', difficulty: '', location: '', duration: '' })

// "1-3" -> min 1, max 3 ; "8+" -> min 8
const durations = [
  { label: 'Any duration', value: '' },
  { label: '1 - 3 days', value: '1-3' },
  { label: '4 - 7 days', value: '4-7' },
  { label: '8+ days', value: '8+' },
]

const bookedIds = computed(() =>
  myBookings.value.filter((b) => b.status !== 'Cancelled').map((b) => b.trek_id),
)
const activeBookings = computed(() => myBookings.value.filter((b) => b.status === 'Booked').length)

async function loadTreks() {
  const params = { q: filters.value.q, difficulty: filters.value.difficulty, location: filters.value.location }
  const d = filters.value.duration
  if (d === '8+') params.duration_min = 8
  else if (d) [params.duration_min, params.duration_max] = d.split('-')
  const res = await api.get('/treks', { params })
  treks.value = res.data
}

async function loadBookings() {
  const res = await api.get('/my-bookings')
  myBookings.value = res.data
}

onMounted(async () => {
  const loc = await api.get('/locations')
  locations.value = loc.data
  loadTreks()
  loadBookings()
})

async function book(t) {
  message.value = ''
  error.value = ''
  try {
    const res = await api.post('/bookings', { trek_id: t.id })
    message.value = res.data.message
  } catch (err) {
    error.value = errorMessage(err)
  }
  loadTreks()
  loadBookings()
}

function clearFilters() {
  filters.value = { q: '', difficulty: '', location: '', duration: '' }
  loadTreks()
}
</script>

<template>
  <div>
    <div class="row g-3 mb-4">
      <div class="col-4"><div class="stat-card"><div class="label">Available treks</div><div class="value">{{ treks.length }}</div></div></div>
      <div class="col-4"><div class="stat-card"><div class="label">Booked treks</div><div class="value">{{ activeBookings }}</div></div></div>
      <div class="col-4"><div class="stat-card"><div class="label">Total history</div><div class="value">{{ myBookings.length }}</div></div></div>
    </div>

    <!-- filters -->
    <div class="card-box mb-4">
      <div class="row g-2">
        <div class="col-md-4"><input v-model="filters.q" @input="loadTreks" class="form-control" placeholder="Search trek or location" /></div>
        <div class="col-6 col-md-2">
          <select v-model="filters.difficulty" @change="loadTreks" class="form-select">
            <option value="">Any difficulty</option><option>Easy</option><option>Moderate</option><option>Hard</option>
          </select>
        </div>
        <div class="col-6 col-md-2">
          <select v-model="filters.location" @change="loadTreks" class="form-select">
            <option value="">Any location</option>
            <option v-for="l in locations" :key="l">{{ l }}</option>
          </select>
        </div>
        <div class="col-6 col-md-2">
          <select v-model="filters.duration" @change="loadTreks" class="form-select">
            <option v-for="d in durations" :key="d.value" :value="d.value">{{ d.label }}</option>
          </select>
        </div>
        <div class="col-6 col-md-2"><button class="btn btn-outline-secondary w-100" @click="clearFilters">Clear</button></div>
      </div>
    </div>

    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

    <div v-if="!treks.length" class="card-box empty">No treks match your search.</div>

    <div class="row g-3">
      <div v-for="t in treks" :key="t.id" class="col-md-6 col-xl-4">
        <div class="trek-card">
          <div class="trek-banner" :class="t.difficulty">
            <span class="badge-soft" :class="'st-' + t.status">{{ t.status }}</span>
          </div>
          <div class="trek-body">
            <h5>{{ t.trek_name }}</h5>
            <div class="trek-meta mb-2">{{ t.location }}</div>
            <p class="small text-muted mb-2">{{ t.description || 'An amazing trekking experience.' }}</p>
            <div class="d-flex flex-wrap gap-2 mb-3">
              <span class="badge-soft" :class="'d-' + t.difficulty">{{ t.difficulty }}</span>
              <span class="badge-soft">{{ t.duration_days }} days</span>
              <span class="badge-soft">{{ t.start_date }}</span>
            </div>
            <div class="d-flex justify-content-between align-items-center mt-auto">
              <div>
                <div class="fw-bold fs-5">₹{{ t.price }}</div>
                <div class="trek-meta">{{ t.available_slots }} slots left</div>
              </div>
              <span v-if="bookedIds.includes(t.id)" class="badge-soft st-Booked">Booked ✓</span>
              <button v-else-if="t.status !== 'Open'" class="btn btn-secondary" disabled>Not open yet</button>
              <button v-else-if="t.available_slots <= 0" class="btn btn-secondary" disabled>Full</button>
              <button v-else class="btn btn-primary" @click="book(t)">Book now</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>