const BASE_URL = 'http://127.0.0.1:8001/api';

export async function generateFullKit({ roleTitle, roleDescription, roleLevel, industry, companySize, remotePolicy }) {
  const response = await fetch(`${BASE_URL}/generate/full-kit/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      role_title: roleTitle,
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

export async function listKits() {
  const response = await fetch(`${BASE_URL}/kits/`);

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

export async function deleteKit(kitId) {
  const response = await fetch(`${BASE_URL}/kits/${kitId}/`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
}

export async function regenerateSection(kitId, sectionName) {
  const response = await fetch(`${BASE_URL}/kits/${kitId}/regenerate-section/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ section_name: sectionName }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}
