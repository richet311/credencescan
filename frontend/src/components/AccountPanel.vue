<script setup>
import { ref } from 'vue'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const username = ref('')
const password = ref('')
const token = ref('')
const history = ref(null)
const error = ref('')
const busy = ref(false)

async function login() {
  error.value = ''
  busy.value = true
  try {
    const response = await fetch(`${apiBaseUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value }),
    })
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Login failed.')
    }

    token.value = data.access_token
    password.value = ''
  } catch (err) {
    error.value = err.message
    console.error('Login failed:', err)
  } finally {
    busy.value = false
  }
}

function logout() {
  token.value = ''
  history.value = null
}

async function loadHistory() {
  error.value = ''
  busy.value = true
  try {
    const response = await fetch(`${apiBaseUrl}/api/documents/history`, {
      headers: { Authorization: `Bearer ${token.value}` },
    })
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Could not load history.')
    }

    history.value = data.history
  } catch (err) {
    error.value = err.message
    console.error('History fetch failed:', err)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="account-panel">
    <h2>Demo login</h2>
    <p class="hint">
      Illustrates a JWT-protected route (analysis history), not a real user
      system.
    </p>

    <template v-if="!token">
      <input v-model="username" type="text" placeholder="username" />
      <input v-model="password" type="password" placeholder="password" />
      <button :disabled="busy" @click="login">Log in</button>
    </template>

    <template v-else>
      <button :disabled="busy" @click="loadHistory">Load analysis history</button>
      <button :disabled="busy" @click="logout">Log out</button>

      <ul v-if="history" class="history">
        <li v-if="!history.length">No analyses recorded yet this session.</li>
        <li v-for="(item, index) in history" :key="index">
          {{ item.filename }} — {{ item.document_type || 'unknown' }}
          ({{ new Date(item.analyzed_at).toLocaleTimeString() }})
        </li>
      </ul>
    </template>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<style scoped>
.account-panel {
  margin-top: 1.5rem;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.hint {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.25rem;
}
input {
  margin-right: 0.5rem;
}
button {
  margin-right: 0.5rem;
}
.history {
  margin-top: 0.75rem;
  padding-left: 1.25rem;
  font-size: 0.9rem;
}
.error {
  color: #b3261e;
  margin-top: 0.75rem;
}
</style>
