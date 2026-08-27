import * as React from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { api, tokenStore } from '@/api/client'
import { auth } from '@/api/endpoints'
import type { User } from '@/api/types'

interface AuthValue {
  user: User | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<User>
  signUp: (body: Parameters<typeof auth.register>[0]) => Promise<User>
  signOut: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = React.createContext<AuthValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null)
  const [loading, setLoading] = React.useState(true)
  const queryClient = useQueryClient()

  const signOut = React.useCallback(() => {
    tokenStore.clear()
    setUser(null)
    queryClient.clear()
  }, [queryClient])

  // Restore the session on first load, and react to a refresh token that
  // expired mid-session (the axios interceptor fires this event).
  React.useEffect(() => {
    let cancelled = false

    async function restore() {
      if (!tokenStore.access()) {
        setLoading(false)
        return
      }
      try {
        const me = await auth.me()
        if (!cancelled) setUser(me)
      } catch {
        if (!cancelled) tokenStore.clear()
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    restore()
    window.addEventListener('jp:signed-out', signOut)
    return () => {
      cancelled = true
      window.removeEventListener('jp:signed-out', signOut)
    }
  }, [signOut])

  const signIn = React.useCallback(async (email: string, password: string) => {
    const tokens = await auth.login({ email, password })
    tokenStore.set(tokens)
    const me = await auth.me()
    setUser(me)
    return me
  }, [])

  const signUp = React.useCallback(
    async (body: Parameters<typeof auth.register>[0]) => {
      await auth.register(body)
      return signIn(body.email, body.password)
    },
    [signIn],
  )

  const refreshUser = React.useCallback(async () => {
    setUser(await auth.me())
  }, [])

  const value = React.useMemo(
    () => ({ user, loading, signIn, signUp, signOut, refreshUser }),
    [user, loading, signIn, signUp, signOut, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthValue {
  const ctx = React.useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}

// Re-exported so callers do not need to reach into the api module directly.
export { api }
