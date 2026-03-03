// In dev: Vite proxy rewrites /api -> localhost:8000
// In prod: frontend served from FastAPI, so '' hits the same origin
const BASE = import.meta.env.DEV ? '/api' : '';

export async function uploadPDF(file) {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

export async function queryDocument(collectionName, question, chatHistory = []) {
  const res = await fetch(`${BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      collection_name: collectionName,
      question,
      chat_history: chatHistory,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Query failed');
  }
  return res.json();
}

export async function getCollections() {
  const res = await fetch(`${BASE}/collections`);
  if (!res.ok) throw new Error('Failed to fetch collections');
  return res.json();
}

export async function deleteCollection(name) {
  const res = await fetch(`${BASE}/collections/${name}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete collection');
  return res.json();
}

export async function healthCheck() {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}
