import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { TokenPair } from './types'

const ACCESS_KEY = 'jp.access'
const REFRESH_KEY = 'jp.refresh'

export const tokenStore = {
  access: () => localStorage.getItem(ACCESS_KEY),
  refresh: () => localStorage.getItem(REFRESH_KEY),
  set(pair: Pick<TokenPair, 'access_token' | 'refresh_token'>) {
    localStorage.setItem(ACCESS_KEY, pair.access_token)
    localStorage.setItem(REFRESH_KEY, pair.refresh_token)
  },
  setAccess(token: string) {
    localStorage.setItem(ACCESS_KEY, token)
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = tokenStore.access()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/** Coalesces parallel 401s onto a single refresh call. */
let refreshing: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const refresh = tokenStore.refresh()
  if (!refresh) return null
  try {
    const { data } = await axios.post<{ access_token: string }>(
      `${api.defaults.baseURL}/auth/refresh`,
      { refresh_token: refresh },
      { headers: { 'Content-Type': 'application/json' } },
    )
    tokenStore.setAccess(data.access_token)
    return data.access_token
  } catch {
    tokenStore.clear()
    return null
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retried?: boolean }
    const isAuthCall = original?.url?.includes('/auth/refresh') || original?.url?.includes('/auth/login')

    if (error.response?.status === 401 && original && !original._retried && !isAuthCall) {
      original._retried = true
      refreshing = refreshing ?? refreshAccessToken().finally(() => { refreshing = null })
      const token = await refreshing
      if (token) {
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      }
      window.dispatchEvent(new CustomEvent('jp:signed-out'))
    }
    return Promise.reject(error)
  },
)

/** Pulls the human-readable message out of a FastAPI error response. */
export function errorMessage(error: unknown, fallback = 'Something went wrong.'): string {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && detail.length) {
      const first = detail[0] as { msg?: string; loc?: string[] }
      if (first?.msg) {
        const field = first.loc?.filter((p) => p !== 'body').join('.')
        return field ? `${field}: ${first.msg}` : first.msg
      }
    }
    if (error.code === 'ERR_NETWORK') {
      return 'Cannot reach the API. Is the backend running?'
    }
  }
  return fallback
}
