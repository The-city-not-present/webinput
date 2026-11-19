import { createApp, ref, onMounted } from 'vue';

import './app.css';

// Error wrapper (see .clinerules/05-js-files.md): surfaces any failure into the
// #errorbanner element instead of letting it vanish in the console.
function logError(e) {
  console.error(e);
  const banner = document.querySelector('#errorbanner');
  if (banner) {
    const p = document.createElement('p');
    p.classList.add('error');
    p.textContent = `${e}`;
    banner.appendChild(p);
  }
}

const App = {
  template: `
<div class="webinput-app">
  <p v-if="loading">Loading questionnaire…</p>
  <p v-else-if="error" class="error">{{ error }}</p>
  <div v-else>
    <p>Questionnaire loaded: {{ fields.length }} top-level field(s).</p>
    <ul>
      <li v-for="f in fields" :key="f.name">{{ f.title }} ({{ f.type }})</li>
    </ul>
  </div>
</div>
`,
  setup() {
    const loading = ref(true);
    const error = ref(null);
    const fields = ref([]);

    async function loadSchema() {
      try {
        const response = await fetch('/schema');
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const schema = await response.json();
        fields.value = Object.entries(schema.properties || {}).map(
          ([name, prop]) => ({
            name,
            title: prop.title || name,
            type: prop['x-type'] || prop.type,
          })
        );
      } catch (e) {
        error.value = `${e}`;
        logError(e);
      } finally {
        loading.value = false;
      }
    }

    onMounted(loadSchema);

    return { loading, error, fields };
  },
};

document.addEventListener('DOMContentLoaded', () => {
  createApp(App).mount('#webinput_app');
});
