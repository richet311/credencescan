<script setup>
import { onMounted, ref } from 'vue'

const status = ref('checking')
const detail = ref('')

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

onMounted(async () => {
  try {
    const response = await fetch(`${apiBaseUrl}/api/health`)
    if (!response.ok) {
      throw new Error(`API responded with status ${response.status}`)
    }
    const data = await response.json()
    status.value = 'connected'
    detail.value = data.service
  } catch (error) {
    status.value = 'unreachable'
    detail.value = error.message
    console.error('Health check failed:', error)
  }
})
</script>

<template>
  <div class="api-status" :class="status">
    <span class="dot"></span>
    <span v-if="status === 'checking'">Checking API connection...</span>
    <span v-else-if="status === 'connected'">API connected ({{ detail }})</span>
    <span v-else>API unreachable — is the backend running? ({{ detail }})</span>
  </div>
</template>

<style scoped>
.api-status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 999px;
  font-size: 0.9rem;
  background: #f1f1f1;
}
.dot {
  width: 0.6rem;
  height: 0.6rem;
  border-radius: 50%;
  background: #999;
}
.connected .dot {
  background: #2ea043;
}
.unreachable .dot {
  background: #d1242f;
}
</style>
