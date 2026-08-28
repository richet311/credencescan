<script setup>
import ApiStatus from './components/ApiStatus.vue'
import UploadForm from './components/UploadForm.vue'
</script>

<template>
  <main class="app">
    <header>
      <h1>CredenceScan</h1>
      <p class="tagline">A privacy-first assistant for reading and understanding financial documents.</p>
    </header>

    <div class="disclaimer">
      This is an independent demo project. It is not affiliated with, endorsed by, or connected
      to any bank or financial institution. All sample documents used here are synthetic.
    </div>

    <ApiStatus />
    <UploadForm />
  </main>
</template>

<style scoped>
.app {
  max-width: 720px;
  margin: 3rem auto;
  padding: 0 1.5rem;
  font-family: system-ui, sans-serif;
}
.tagline {
  color: #555;
}
.disclaimer {
  font-size: 0.85rem;
  color: #6a4d00;
  background: #fff6e0;
  border: 1px solid #f0d98a;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
}
</style>
