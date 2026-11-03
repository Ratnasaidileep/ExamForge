export interface DemoProfile {
  id: string;
  name: string;
  role: 'faculty' | 'student';
  email: string;
  department?: string;
  avatar_url?: string;
}

const STORAGE_KEY_USER = 'examforge_demo_user';
const STORAGE_KEY_ROLE = 'examforge_demo_role';

export function getActiveUser(): DemoProfile {
  try {
    const saved = localStorage.getItem(STORAGE_KEY_USER);
    if (saved) return JSON.parse(saved);
  } catch (e) {
    // fallback
  }
  return {
    id: 'prof_sharma',
    name: 'Dr. R. Sharma',
    role: 'faculty',
    email: 'r.sharma@college.edu',
    department: 'Computer Science & Engineering',
    avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'
  };
}

export function setActiveUser(user: DemoProfile) {
  localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(user));
  localStorage.setItem(STORAGE_KEY_ROLE, user.role);
  window.dispatchEvent(new Event('examforge_role_changed'));
}

export async function apiFetch<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const user = getActiveUser();
  const headers = new Headers(options.headers || {});
  
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  
  headers.set('X-Demo-Role', user.role);
  headers.set('X-Demo-User-Id', user.id);
  
  const url = endpoint.startsWith('http') ? endpoint : `/api/v1${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  const res = await fetch(url, {
    ...options,
    headers
  });
  
  if (!res.ok) {
    let errorMsg = `Request failed (${res.status})`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.error || errorMsg;
    } catch {
      // not json
    }
    throw new Error(errorMsg);
  }
  
  // Handle empty or blob/pdf responses
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return res.json();
  }
  return res as any;
}
