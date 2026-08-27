import * as React from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { errorMessage } from '@/api/client'
import { auth } from '@/api/endpoints'
import { useAuth } from '@/context/AuthContext'
import { SkillInput } from '@/components/SkillInput'
import { Alert, Button, Card, Field, Input } from '@/components/ui'

export function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const queryClient = useQueryClient()

  const candidate = user?.candidate_profile
  const recruiter = user?.recruiter_profile

  const [fullName, setFullName] = React.useState(candidate?.full_name ?? '')
  const [headline, setHeadline] = React.useState(candidate?.headline ?? '')
  const [skills, setSkills] = React.useState<string[]>(candidate?.skills ?? [])
  const [resumeUrl, setResumeUrl] = React.useState(candidate?.resume_url ?? '')
  const [companyName, setCompanyName] = React.useState(recruiter?.company_name ?? '')
  const [companyWebsite, setCompanyWebsite] = React.useState(recruiter?.company_website ?? '')

  const [error, setError] = React.useState<string | null>(null)
  const [saved, setSaved] = React.useState(false)
  const [busy, setBusy] = React.useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    setSaved(false)
    try {
      await auth.updateProfile(
        user?.role === 'candidate'
          ? { full_name: fullName, headline, skills, resume_url: resumeUrl }
          : { company_name: companyName, company_website: companyWebsite },
      )
      await refreshUser()
      // Skills feed the AI suggestions, so the cached list is now stale.
      queryClient.invalidateQueries({ queryKey: ['suggestions'] })
      setSaved(true)
    } catch (err) {
      setError(errorMessage(err, 'Could not save your profile.'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-1 text-2xl font-semibold tracking-tight">Your profile</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        {user?.role === 'candidate'
          ? 'Your skills drive the roles we recommend to you.'
          : 'This is what candidates see on your job posts.'}
      </p>

      <Card className="p-6">
        <form onSubmit={onSubmit} className="space-y-5">
          {error ? <Alert>{error}</Alert> : null}
          {saved ? <Alert tone="success">Profile saved.</Alert> : null}

          {user?.role === 'candidate' ? (
            <>
              <Field label="Full name">
                <Input value={fullName} onChange={(e) => setFullName(e.target.value)} />
              </Field>
              <Field label="Headline" hint="A one-line summary, e.g. “Frontend engineer, 5 years React”.">
                <Input value={headline} onChange={(e) => setHeadline(e.target.value)} />
              </Field>
              <Field label="Skills" hint="These are matched against each job's requirements.">
                <SkillInput value={skills} onChange={setSkills} />
              </Field>
              <Field label="Resume link" hint="A public URL — file upload is not part of this version.">
                <Input type="url" placeholder="https://…" value={resumeUrl}
                       onChange={(e) => setResumeUrl(e.target.value)} />
              </Field>
            </>
          ) : (
            <>
              <Field label="Company name">
                <Input value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
              </Field>
              <Field label="Company website">
                <Input type="url" placeholder="https://…" value={companyWebsite}
                       onChange={(e) => setCompanyWebsite(e.target.value)} />
              </Field>
            </>
          )}

          <div className="flex items-center gap-3">
            <Button type="submit" loading={busy}>Save changes</Button>
            <span className="text-sm text-muted-foreground">{user?.email}</span>
          </div>
        </form>
      </Card>
    </div>
  )
}
