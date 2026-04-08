const BASE_URL = 'http://127.0.0.1:8001/api';

function authHeaders(token) {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Token ${token}`,
  };
}

export async function loginManager(username, password) {
  const response = await fetch(`${BASE_URL}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Login failed');
  }
  return response.json();
}

export async function logoutManager(token) {
  const response = await fetch(`${BASE_URL}/auth/logout/`, {
    method: 'POST',
    headers: authHeaders(token),
  });
  if (!response.ok) {
    throw new Error(`Logout failed with status ${response.status}`);
  }
}

export async function generateFullKit(token, { roleDescription, roleLevel, industry, companySize, remotePolicy }) {
  const response = await fetch(`${BASE_URL}/generate/full-kit/`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({
      role_description: roleDescription,
      role_level: roleLevel || '',
      industry: industry || '',
      company_size: companySize || '',
      remote_policy: remotePolicy || '',
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = Object.values(errorData).flat().join(' ') || `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}

export async function listKits(token) {
  const headers = token ? { 'Authorization': `Token ${token}` } : {};
  const response = await fetch(`${BASE_URL}/kits/`, { headers });
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function getKit(kitId) {
  const response = await fetch(`${BASE_URL}/kits/${kitId}/`);
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function deleteKit(token, kitId) {
  const response = await fetch(`${BASE_URL}/kits/${kitId}/`, {
    method: 'DELETE',
    headers: { 'Authorization': `Token ${token}` },
  });
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
}

export async function publishKit(token, kitId, newStatus) {
  const response = await fetch(`${BASE_URL}/kits/${kitId}/publish/`, {
    method: 'PATCH',
    headers: authHeaders(token),
    body: JSON.stringify({ status: newStatus }),
  });
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function updateKit(token, kitId, data) {
  const response = await fetch(`${BASE_URL}/kits/${kitId}/`, {
    method: 'PATCH',
    headers: authHeaders(token),
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function regenerateSection(token, kitId, sectionName) {
  const response = await fetch(`${BASE_URL}/kits/${kitId}/regenerate-section/`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ section_name: sectionName }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function matchCv(kitId, file) {
  const formData = new FormData();
  formData.append('cv_file', file);
  const response = await fetch(`${BASE_URL}/kits/${kitId}/match-cv/`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }
  return response.json();
}
