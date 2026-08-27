import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/context/AuthContext'
import { messages } from '@/api/endpoints'
import { Avatar } from '@/components/Avatar'
import { Badge, Button } from '@/components/ui'
import { cn } from '@/lib/cn'

function navClass({ isActive }: { isActive: boolean }) {
  return cn(
    'rounded-md px-3 py-2 text-sm font-medium transition-colors',
    isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground hover:text-foreground',
  )
}

export function Layout() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  const { data: unread } = useQuery({
    queryKey: ['unread'],
    queryFn: messages.unreadCount,
    enabled: Boolean(user),
    // US-4.3: polling is enough for MVP — no WebSocket.
    refetchInterval: 20_000,
    refetchOnWindowFocus: true,
  })

  const unreadCount = unread?.unread ?? 0

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-6xl items-center gap-1 px-4">
          <NavLink to="/" className="mr-4 text-base font-semibold tracking-tight">
            Job&nbsp;Portal
          </NavLink>

          <NavLink to="/jobs" className={navClass}>Jobs</NavLink>

          {user?.role === 'candidate' ? (
            <>
              <NavLink to="/dashboard" className={navClass}>For you</NavLink>
              <NavLink to="/applications" className={navClass}>
                <span className="inline-flex items-center gap-1.5">
                  Applications
                  {unreadCount > 0 ? <Badge tone="accent">{unreadCount}</Badge> : null}
                </span>
              </NavLink>
            </>
          ) : null}

          {user?.role === 'recruiter' ? (
            <NavLink to="/my-jobs" className={navClass}>
              <span className="inline-flex items-center gap-1.5">
                My jobs
                {unreadCount > 0 ? <Badge tone="accent">{unreadCount}</Badge> : null}
              </span>
            </NavLink>
          ) : null}

          <div className="ml-auto flex items-center gap-2">
            {user ? (
              <>
                <NavLink to="/profile" className={navClass}>
                  <span className="inline-flex items-center gap-2">
                    <Avatar
                      size="sm"
                      src={user.candidate_profile?.avatar_url
                        ?? user.recruiter_profile?.avatar_url}
                      name={user.candidate_profile?.full_name
                        ?? user.recruiter_profile?.company_name
                        ?? user.email}
                    />
                    <span className="hidden sm:inline">
                      {user.candidate_profile?.full_name
                        || user.recruiter_profile?.company_name
                        || user.email}
                    </span>
                  </span>
                </NavLink>
                <Button variant="ghost" size="sm" onClick={() => { signOut(); navigate('/login') }}>
                  Sign out
                </Button>
              </>
            ) : (
              <>
                <Button variant="ghost" size="sm" onClick={() => navigate('/login')}>Sign in</Button>
                <Button size="sm" onClick={() => navigate('/register')}>Create account</Button>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
