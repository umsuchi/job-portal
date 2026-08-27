import * as React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { errorMessage } from '@/api/client'
import { useAuth } from '@/context/AuthContext'
import { Alert, Button, Card, Field, Input } from '@/components/ui'

export function LoginPage() {
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [error, setError] = React.useState<string | null>(null)
  const [busy, setBusy] = React.useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const me = await signIn(email, password)
      const from = (location.state as { from?: string } | null)?.from
      navigate(from ?? (me.role === 'candidate' ? '/dashboard' : '/my-jobs'), { replace: true })
    } catch (err) {
      setError(errorMessage(err, 'Could not sign you in.'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <h1 className="mb-1 text-2xl font-semibold tracking-tight">Welcome back</h1>
      <p className="mb-6 text-sm text-muted-foreground">Sign in to continue.</p>

      <Card className="p-6">
        <form onSubmit={onSubmit} className="space-y-4">
          {error ? <Alert>{error}</Alert> : null}

          <Field label="Email">
            <Input type="email" autoComplete="email" required value={email}
                   onChange={(e) => setEmail(e.target.value)} />
          </Field>

          <Field label="Password">
            <Input type="password" autoComplete="current-password" required value={password}
                   onChange={(e) => setPassword(e.target.value)} />
          </Field>

          <Button type="submit" className="w-full" loading={busy}>Sign in</Button>
        </form>
      </Card>

      <p className="mt-4 text-center text-sm text-muted-foreground">
        No account yet? <Link to="/register" className="font-medium text-foreground hover:underline">Create one</Link>
      </p>
    </div>
  )
}
