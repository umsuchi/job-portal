import * as React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { errorMessage } from '@/api/client'
import { useAuth } from '@/context/AuthContext'
import { Alert, Button, Card, Field, Input } from '@/components/ui'
import { cn } from '@/lib/cn'
import type { Role } from '@/api/types'

const ROLE_COPY: Record<Role, { title: string; blurb: string }> = {
  candidate: { title: 'I am looking for work', blurb: 'Browse jobs, apply, and get AI-matched suggestions.' },
  recruiter: { title: 'I am hiring', blurb: 'Post roles and review applicants.' },
}

export function RegisterPage() {
  const { signUp } = useAuth()
  const navigate = useNavigate()
  const [role, setRole] = React.useState<Role>('candidate')
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [name, setName] = React.useState('')
  const [error, setError] = React.useState<string | null>(null)
  const [busy, setBusy] = React.useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await signUp({
        email,
        password,
        role,
        ...(role === 'candidate' ? { full_name: name } : { company_name: name }),
      })
      navigate(role === 'candidate' ? '/profile' : '/my-jobs', { replace: true })
    } catch (err) {
      setError(errorMessage(err, 'Could not create your account.'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <h1 className="mb-1 text-2xl font-semibold tracking-tight">Create your account</h1>
      <p className="mb-6 text-sm text-muted-foreground">Pick how you will use the portal.</p>

      <Card className="p-6">
        <form onSubmit={onSubmit} className="space-y-4">
          {error ? <Alert>{error}</Alert> : null}

          <div className="grid gap-2 sm:grid-cols-2">
            {(Object.keys(ROLE_COPY) as Role[]).map((option) => (
              <button
                key={option}
                type="button"
                aria-pressed={role === option}
                onClick={() => setRole(option)}
                className={cn(
                  'rounded-md border p-3 text-left transition-colors',
                  role === option
                    ? 'border-primary bg-accent'
                    : 'border-input hover:border-muted-foreground/40',
                )}
              >
                <span className="block text-sm font-medium">{ROLE_COPY[option].title}</span>
                <span className="mt-0.5 block text-xs text-muted-foreground">
                  {ROLE_COPY[option].blurb}
                </span>
              </button>
            ))}
          </div>

          <Field label={role === 'candidate' ? 'Full name' : 'Company name'}>
            <Input required value={name} onChange={(e) => setName(e.target.value)} />
          </Field>

          <Field label="Email">
            <Input type="email" autoComplete="email" required value={email}
                   onChange={(e) => setEmail(e.target.value)} />
          </Field>

          <Field label="Password" hint="At least 8 characters.">
            <Input type="password" autoComplete="new-password" required minLength={8}
                   value={password} onChange={(e) => setPassword(e.target.value)} />
          </Field>

          <Button type="submit" className="w-full" loading={busy}>Create account</Button>
        </form>
      </Card>

      <p className="mt-4 text-center text-sm text-muted-foreground">
        Already registered? <Link to="/login" className="font-medium text-foreground hover:underline">Sign in</Link>
      </p>
    </div>
  )
}
