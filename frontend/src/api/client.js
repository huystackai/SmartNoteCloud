const API_BASE = '/api';
const TOKEN_KEY = 'minddeck_token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers
  };

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    let detail = 'Request failed';
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch {
      detail = response.statusText;
    }
    throw new Error(Array.isArray(detail) ? detail.map((item) => item.msg).join(', ') : detail);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  register: (payload) => request('/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
  login: async (username, password) => {
    const form = new FormData();
    form.append('username', username);
    form.append('password', password);
    return request('/auth/login', { method: 'POST', body: form });
  },
  me: () => request('/auth/me'),
  bootstrap: () => request('/mind/bootstrap'),
  page: (id) => request(`/mind/pages/${id}`),
  createPage: (payload) => request('/mind/pages', { method: 'POST', body: JSON.stringify(payload) }),
  updatePage: (id, payload) => request(`/mind/pages/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),
  deletePage: (id) => request(`/mind/pages/${id}`, { method: 'DELETE' }),
  saveBlocks: (pageId, blocks) =>
    request(`/mind/pages/${pageId}/blocks`, { method: 'PUT', body: JSON.stringify({ blocks }) }),
  summarizePage: (pageId) => request(`/mind/pages/${pageId}/summarize`, { method: 'POST' }),
  generateCards: (pageId) => request(`/mind/pages/${pageId}/generate-cards`, { method: 'POST' }),
  createDeck: (payload) => request('/mind/decks', { method: 'POST', body: JSON.stringify(payload) }),
  deckCards: (deckId, due = false) => request(`/mind/decks/${deckId}/cards${due ? '?due=true' : ''}`),
  createCard: (payload) => request('/mind/cards', { method: 'POST', body: JSON.stringify(payload) }),
  reviewCard: (payload) => request('/mind/reviews', { method: 'POST', body: JSON.stringify(payload) }),
  stats: () => request('/mind/stats'),
  search: (q) => request(`/mind/search?q=${encodeURIComponent(q)}`),
  adminStats: () => request('/admin/stats'),
  adminUsers: () => request('/admin/users'),
  adminIPAddresses: () => request('/admin/ip-addresses'),
  lockUser: (id) => request(`/admin/users/${id}/lock`, { method: 'POST' }),
  unlockUser: (id) => request(`/admin/users/${id}/unlock`, { method: 'POST' }),
  blockIP: (payload) => request('/admin/ip-blocks', { method: 'POST', body: JSON.stringify(payload) }),
  unblockIP: (ipAddress) => request(`/admin/ip-blocks/${encodeURIComponent(ipAddress)}`, { method: 'DELETE' })
};
