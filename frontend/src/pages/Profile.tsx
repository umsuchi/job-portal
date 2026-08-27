import * as React from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { errorMessage } from '@/api/client'
import { auth } from '@/api/endpoints'
import { useAuth } from '@/context/AuthContext'
import { Avatar } from '@/components/Avatar'
import { CheckboxGroup } from '@/components/CheckboxGroup'
import { SkillInput } from '@/components/SkillInput'
import { Alert, Button, Card, CardContent, CardHeader, CardTitle, Field, Input, Select, Textarea } from '@/components/ui'
import { EXPERIENCE_LABELS, JOB_TYPE_LABELS, WORK_MODE_LABELS } from '@/lib/format'
import type { ExperienceLevel, JobType, WorkMode } from '@/api/types'

/** Locations are a plain comma-separated field — they are free text, not a taxonomy. */
function LocationsInput({
  value, onChange,
}: { value: string[]; onChange: (next: string[]) => void }) {
  const [draft, setDraft] = React.useState(value.join(', '))
  React.useEffect(() => { setDraft(value.join(', ')) }, [value.join('|')])

  return (
    <Input
      value={draft}
      placeholder="Remote, Dhaka, Singapore"
      onChange={(e) => setDraft(e.target.value)}
      onBlur={() => onChange(draft.split(',').map((s) => s.trim()).filter(Boolean))}
    />
  )
}

export function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const queryClient = useQueryClient()

  const candidate = user?.candidate_profile
  const recruiter = user?.recruiter_profile
  const isCandidate = user?.role === 'candidate'

  // --- candidate state ------------------------------------------------------
  const [fullName, setFullName] = React.useState(candidate?.full_name ?? '')
  const [headline, setHeadline] = React.useState(candidate?.headline ?? '')
  const [bio, setBio] = React.useState(candidate?.bio ?? '')
  const [avatarUrl, setAvatarUrl] = React.useState(
    candidate?.avatar_url ?? recruiter?.avatar_url ?? '')
  const [resumeUrl, setResumeUrl] = React.useState(candidate?.resume_url ?? '')
  const [location, setLocation] = React.useState(candidate?.location ?? '')
  const [skills, setSkills] = React.useState<string[]>(candidate?.skills ?? [])
  const [years, setYears] = React.useState(candidate?.years_experience?.toString() ?? '')
  const [level, setLevel] = React.useState<ExperienceLevel | ''>(
    candidate?.experience_level ?? '')
  const [jobTypes, setJobTypes] = React.useState<JobType[]>(
    candidate?.preferred_job_types ?? [])
  const [workModes, setWorkModes] = React.useState<WorkMode[]>(
    candidate?.preferred_work_modes ?? [])
  const [locations, setLocations] = React.useState<string[]>(
    candidate?.preferred_locations ?? [])
  const [salary, setSalary] = React.useState(
    candidate?.desired_salary_min?.toString() ?? '')
  const [openToWork, setOpenToWork] = React.useState(candidate?.open_to_work ?? true)

  // --- recruiter state ------------------------------------------------------
  const [companyName, setCompanyName] = React.useState(recruiter?.company_name ?? '')
  const [companyWebsite, setCompanyWebsite] = React.useState(recruiter?.company_website ?? '')
  const [about, setAbout] = React.useState(recruiter?.about ?? '')
  const [industry, setIndustry] = React.useState(recruiter?.industry ?? '')
  const [headquarters, setHeadquarters] = React.useState(recruiter?.headquarters ?? '')

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
        isCandidate
          ? {
              full_name: fullName, headline, bio, avatar_url: avatarUrl,
              resume_url: resumeUrl, location, skills,
              years_experience: years === '' ? null : Number(years),
              experience_level: level || null,
              preferred_job_types: jobTypes,
              preferred_work_modes: workModes,
              preferred_locations: locations,
              desired_salary_min: salary === '' ? null : Number(salary),
              open_to_work: openToWork,
            }
          : {
              company_name: companyName, company_website: companyWebsite,
              avatar_url: avatarUrl, about, industry, headquarters,
            },
      )
      await refreshUser()
      // Anything the matcher reads has changed, so cached suggestions are stale.
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
        {isCandidate
          ? 'Everything here feeds the roles we recommend to you — not just your skills.'
          : 'This is what candidates see on your job posts.'}
      </p>

      <form onSubmit={onSubmit} className="space-y-6">
        {error ? <Alert>{error}</Alert> : null}
        {saved ? <Alert tone="success">Profile saved.</Alert> : null}

        <Card>
          <CardHeader><CardTitle>{isCandidate ? 'About you' : 'Company'}</CardTitle></CardHeader>
          <CardContent className="space-y-5">
            <div className="flex items-center gap-4">
              <Avatar
                size="lg"
                src={avatarUrl}
                name={isCandidate ? fullName : companyName}
              />
              <div className="flex-1">
                <Field
                  label={isCandidate ? 'Profile picture URL' : 'Company logo URL'}
                  hint="Paste a link to an image. Falls back to initials if it will not load."
                >
                  <Input
                    type="url" placeholder="https://…" value={avatarUrl}
                    onChange={(e) => setAvatarUrl(e.target.value)}
                  />
                </Field>
              </div>
            </div>

            {isCandidate ? (
              <>
                <Field label="Full name">
                  <Input value={fullName} onChange={(e) => setFullName(e.target.value)} />
                </Field>
                <Field label="Headline" hint="One line, e.g. “Frontend engineer, 5 years React”.">
                  <Input value={headline} onChange={(e) => setHeadline(e.target.value)} />
                </Field>
                <Field label="About" hint="A short summary. Recruiters read it, and it gives the recommendation engine context beyond your tags.">
                  <Textarea
                    className="min-h-[120px]" maxLength={4000} value={bio}
                    onChange={(e) => setBio(e.target.value)}
                  />
                </Field>
                <Field label="Where you are based">
                  <Input
                    value={location} placeholder="Dhaka, Bangladesh"
                    onChange={(e) => setLocation(e.target.value)}
                  />
                </Field>
                <Field label="Resume link" hint="A public URL — file upload is not part of this version.">
                  <Input
                    type="url" placeholder="https://…" value={resumeUrl}
                    onChange={(e) => setResumeUrl(e.target.value)}
                  />
                </Field>
              </>
            ) : (
              <>
                <Field label="Company name">
                  <Input value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
                </Field>
                <Field label="Website">
                  <Input
                    type="url" placeholder="https://…" value={companyWebsite}
                    onChange={(e) => setCompanyWebsite(e.target.value)}
                  />
                </Field>
                <Field label="Industry">
                  <Input
                    value={industry} placeholder="Developer tooling"
                    onChange={(e) => setIndustry(e.target.value)}
                  />
                </Field>
                <Field label="Headquarters">
                  <Input
                    value={headquarters} placeholder="Amsterdam, Netherlands"
                    onChange={(e) => setHeadquarters(e.target.value)}
                  />
                </Field>
                <Field label="About the company" hint="Shown on every job you post.">
                  <Textarea
                    className="min-h-[120px]" maxLength={4000} value={about}
                    onChange={(e) => setAbout(e.target.value)}
                  />
                </Field>
              </>
            )}
          </CardContent>
        </Card>

        {isCandidate ? (
          <>
            <Card>
              <CardHeader><CardTitle>Experience</CardTitle></CardHeader>
              <CardContent className="space-y-5">
                <Field label="Skills" hint="Matched against each job's requirements.">
                  <SkillInput value={skills} onChange={setSkills} />
                </Field>
                <div className="grid gap-4 sm:grid-cols-2">
                  <Field label="Years of experience">
                    <Input
                      type="number" min={0} max={60} value={years}
                      onChange={(e) => setYears(e.target.value)}
                    />
                  </Field>
                  <Field label="Level" hint="Left blank, we infer it from your years.">
                    <Select
                      value={level}
                      onChange={(e) => setLevel(e.target.value as ExperienceLevel | '')}
                    >
                      <option value="">Infer from years</option>
                      {Object.entries(EXPERIENCE_LABELS).map(([key, label]) => (
                        <option key={key} value={key}>{label}</option>
                      ))}
                    </Select>
                  </Field>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>What you are looking for</CardTitle>
                <p className="text-sm text-muted-foreground">
                  These rank your recommendations. Leave any of them blank and it simply
                  stops being scored.
                </p>
              </CardHeader>
              <CardContent className="space-y-5">
                <Field label="Work arrangement">
                  <CheckboxGroup
                    options={WORK_MODE_LABELS} value={workModes} onChange={setWorkModes}
                  />
                </Field>
                <Field label="Employment type">
                  <CheckboxGroup
                    options={JOB_TYPE_LABELS} value={jobTypes} onChange={setJobTypes}
                  />
                </Field>
                <Field label="Preferred locations" hint="Comma separated. Remote roles always match.">
                  <LocationsInput value={locations} onChange={setLocations} />
                </Field>
                <Field label="Minimum salary" hint="Roles paying below this are ranked lower, never hidden.">
                  <Input
                    type="number" min={0} value={salary} placeholder="80000"
                    onChange={(e) => setSalary(e.target.value)}
                  />
                </Field>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox" checked={openToWork}
                    onChange={(e) => setOpenToWork(e.target.checked)}
                    className="h-4 w-4 rounded border-input"
                  />
                  I am open to new opportunities
                </label>
              </CardContent>
            </Card>
          </>
        ) : null}

        <div className="flex items-center gap-3">
          <Button type="submit" loading={busy}>Save changes</Button>
          <span className="text-sm text-muted-foreground">{user?.email}</span>
        </div>
      </form>
    </div>
  )
}
