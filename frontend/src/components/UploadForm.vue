<script setup>
import { ref } from 'vue'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const selectedFile = ref(null)
const result = ref(null)
const error = ref('')
const submitting = ref(false)

function onFileChange(event) {
  selectedFile.value = event.target.files[0] || null
  result.value = null
  error.value = ''
}

async function onSubmit() {
  if (!selectedFile.value) {
    error.value = 'Choose a PDF, PNG, or JPEG file first.'
    return
  }

  submitting.value = true
  result.value = null
  error.value = ''

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const response = await fetch(`${apiBaseUrl}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    })
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || `Upload failed with status ${response.status}`)
    }

    result.value = data
  } catch (err) {
    error.value = err.message
    console.error('Upload failed:', err)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="upload-form">
    <h2>Try a sample document</h2>
    <p class="hint">
      PDF, PNG, or JPEG only. The original file is never stored; only the
      insights below are kept in an in-memory history for this session.
    </p>

    <input type="file" accept=".pdf,.png,.jpg,.jpeg" @change="onFileChange" />
    <button :disabled="submitting" @click="onSubmit">
      {{ submitting ? 'Uploading...' : 'Upload' }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="result" class="result">
      <p>
        <strong>Document type:</strong> {{ result.document_type || 'unknown' }}
        <span v-if="result.confidence" class="muted">
          ({{ (result.confidence * 100).toFixed(1) }}% confidence)
        </span>
      </p>

      <ul v-if="Object.keys(result.fields || {}).length" class="fields">
        <li v-for="(value, key) in result.fields" :key="key">
          {{ key.replaceAll('_', ' ') }}: ${{ value.toFixed(2) }}
        </li>
      </ul>

      <ul class="insights">
        <li v-for="(insight, index) in result.insights" :key="index">{{ insight }}</li>
      </ul>

      <details>
        <summary>Raw extracted text</summary>
        <pre>{{ result.extracted_text }}</pre>
      </details>
    </div>
  </div>
</template>

<style scoped>
.upload-form {
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
button {
  margin-left: 0.75rem;
}
.error {
  color: #b3261e;
  margin-top: 0.75rem;
}
.result {
  background: #f4f3ec;
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 0.75rem;
  font-size: 0.9rem;
}
.muted {
  color: #666;
  font-size: 0.85rem;
}
.fields,
.insights {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
}
.result pre {
  white-space: pre-wrap;
  font-size: 0.8rem;
}
</style>
