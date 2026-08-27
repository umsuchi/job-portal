import * as React from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { errorMessage } from '@/api/client'
import { jobs } from '@/api/endpoints'
import { BulletListInput } from '@/components/BulletListInput'
import { SkillInput } from '@/components/SkillInput'
import {
  Alert, Button, Card, CardContent, CardHeader, CardTitle, Field, Input, Select, Skeleton, Textarea,
} from '@/components/ui'
import { EXPERIENCE_LABELS, JOB_TYPE_LABELS, WORK_MODE_LABELS } from '@/lib/format'
import type { ExperienceLevel, JobType, WorkMode } from '@/api/types'

interface FormState {
  title: string
  description: string
  responsibilities: string[]
  requirements: string[]
  benefits: string[]
  required_skills: string[]
  nice_to_have_skills: string[]
  experience_level: ExperienceLevel
  min_years_experience: string
  location: string
  job_type: JobType
  work_mode: WorkMode
  salary_min: string
  salary_max: string
  salary_currency: string
  application_deadline: string
}

const EMPTY: FormState = {
  title: '', description: '', responsibilities: [], requirements: [], benefits: [],
  required_skills: [], nice_to_have_skills: [], experience_level: 'mid',
  min_years_experience: '', location: '', job_type: 'full_time', work_mode: 'onsite',
  salary_min: '', salary_max: '', salary_currency: 'USD', application_deadline: '',
}

export function JobFormPage() {
  const { jobId } = useParams()
  const isEdit = Boolean(jobId)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [form, setForm] = React.useState<FormState>(EMPTY)
  const [error, setError] = React.useState<string | null>(null)
  const [hydrated, setHydrated] = React.useState(!isEdit)

  const { data: existing, isPending } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobs.get(jobId!),
    enabled: isEdit,
  })

  // Seed the form once the existing post arrives.
  React.useEffect(() => {
    if (!existing || hydrated) return
    setForm({
      title: existing.title,
      description: existing.description,
      responsibilities: existing.responsibilities,
      requirements: existing.requirements,
      benefits: existing.benefits,
      required_skills: existing.required_skills,
      nice_to_have_skills: existing.nice_to_have_skills,
      experience_level: existing.experience_level,
      min_years_experience: existing.min_years_experience?.toString() ?? '',
      location: existing.location,
      job_type: existing.job_type,
      work_mode: existing.work_mode,
      salary_min: existing.salary_min?.toString() ?? '',
      salary_max: existing.salary_max?.toString() ?? '',
      salary_currency: existing.salary_currency,
      application_deadline: existing.application_deadline ?? '',
    })
    setHydrated(true)
  }, [existing, hydrated])

  const save = useMutation({
    mutationFn: () => {
      const body = {
        title: form.title,
        description: form.description,
        responsibilities: form.responsibilities.filter(Boolean),
        requirements: form.requirements.filter(Boolean),
        benefits: form.benefits.filter(Boolean),
        required_skills: form.required_skills,
        nice_to_have_skills: form.nice_to_have_skills,
        experience_level: form.experience_level,
        min_years_experience:
          form.min_years_experience === '' ? null : Number(form.min_years_experience),
        location: form.location,
        job_type: form.job_type,
        work_mode: form.work_mode,
        salary_min: form.salary_min ? Number(form.salary_min) : null,
        salary_max: form.salary_max ? Number(form.salary_max) : null,
        salary_currency: form.salary_currency,
        application_deadline: form.application_deadline || null,
      }
      return isEdit ? jobs.update(jobId!, body) : jobs.create(body)
    },
    onSuccess: (job) => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['job', job.id] })
      navigate('/my-jobs')
    },
    onError: (err) => setError(errorMessage(err, 'Could not save the job post.')),
  })

  function set<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((f) => ({ ...f, [key]: value }))
  }

  if (isEdit && isPending) return <Skeleton className="h-96 w-full" />

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-1 text-2xl font-semibold tracking-tight">
        {isEdit ? 'Edit job post' : 'Post a job'}
      </h1>
      <p className="mb-6 text-sm text-muted-foreground">
        The more you fill in, the better we can match candidates to it.
      </p>

      <form
        className="space-y-6"
        onSubmit={(e) => { e.preventDefault(); setError(null); save.mutate() }}
      >
        {error ? <Alert>{error}</Alert> : null}

        <Card>
          <CardHeader><CardTitle>The role</CardTitle></CardHeader>
          <CardContent className="space-y-5">
            <Field label="Title">
              <Input
                required minLength={2} value={form.title}
                placeholder="Senior React Engineer"
                onChange={(e) => set('title', e.target.value)}
              />
            </Field>
            <Field label="Description" hint="Two or three sentences on what the role is and who it suits.">
              <Textarea
                required minLength={10} className="min-h-[140px]" value={form.description}
                placeholder="What the role involves, who you are looking for…"
                onChange={(e) => set('description', e.target.value)}
              />
            </Field>
            <Field label="Responsibilities" hint="Optional. One per line.">
              <BulletListInput
                value={form.responsibilities}
                onChange={(next) => set('responsibilities', next)}
                placeholder="Own the architecture of our main application"
                addLabel="Add responsibility"
              />
            </Field>
            <Field label="Requirements" hint="Optional. What a candidate needs, in prose.">
              <BulletListInput
                value={form.requirements}
                onChange={(next) => set('requirements', next)}
                placeholder="5+ years building production React applications"
                addLabel="Add requirement"
              />
            </Field>
            <Field label="Benefits" hint="Optional.">
              <BulletListInput
                value={form.benefits}
                onChange={(next) => set('benefits', next)}
                placeholder="Fully remote within ±3 hours of CET"
                addLabel="Add benefit"
              />
            </Field>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Who it is for</CardTitle>
            <p className="text-sm text-muted-foreground">
              Required skills drive matching. Nice-to-haves widen the net without
              excluding anyone.
            </p>
          </CardHeader>
          <CardContent className="space-y-5">
            <Field label="Required skills" hint="At least one.">
              <SkillInput
                value={form.required_skills}
                onChange={(next) => set('required_skills', next)}
                placeholder="React, TypeScript, PostgreSQL…"
              />
            </Field>
            <Field label="Nice-to-have skills" hint="Optional. Scored lower than required ones.">
              <SkillInput
                value={form.nice_to_have_skills}
                onChange={(next) => set('nice_to_have_skills', next)}
                placeholder="Storybook, Design Systems…"
              />
            </Field>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Experience level">
                <Select
                  value={form.experience_level}
                  onChange={(e) => set('experience_level', e.target.value as ExperienceLevel)}
                >
                  {Object.entries(EXPERIENCE_LABELS).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </Select>
              </Field>
              <Field label="Minimum years" hint="Optional.">
                <Input
                  type="number" min={0} max={40} value={form.min_years_experience}
                  onChange={(e) => set('min_years_experience', e.target.value)}
                />
              </Field>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Where and how</CardTitle></CardHeader>
          <CardContent className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Location">
                <Input
                  required value={form.location} placeholder="Remote / Berlin / Dhaka"
                  onChange={(e) => set('location', e.target.value)}
                />
              </Field>
              <Field label="Work arrangement">
                <Select
                  value={form.work_mode}
                  onChange={(e) => set('work_mode', e.target.value as WorkMode)}
                >
                  {Object.entries(WORK_MODE_LABELS).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </Select>
              </Field>
              <Field label="Employment type">
                <Select
                  value={form.job_type}
                  onChange={(e) => set('job_type', e.target.value as JobType)}
                >
                  {Object.entries(JOB_TYPE_LABELS).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </Select>
              </Field>
            </div>

            <Field
              label="Application deadline"
              hint="Optional. Applications are accepted all through this day; after it the post shows as expired and stops accepting them."
            >
              <Input
                type="date"
                value={form.application_deadline}
                // Only constrained on create — an expired post must stay editable.
                min={isEdit ? undefined : new Date().toISOString().slice(0, 10)}
                onChange={(e) => set('application_deadline', e.target.value)}
              />
            </Field>

            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Salary minimum" hint="Optional.">
                <Input
                  type="number" min={0} value={form.salary_min}
                  onChange={(e) => set('salary_min', e.target.value)}
                />
              </Field>
              <Field label="Salary maximum" hint="Optional.">
                <Input
                  type="number" min={0} value={form.salary_max}
                  onChange={(e) => set('salary_max', e.target.value)}
                />
              </Field>
              <Field label="Currency">
                <Select
                  value={form.salary_currency}
                  onChange={(e) => set('salary_currency', e.target.value)}
                >
                  {['USD', 'EUR', 'GBP', 'SGD', 'AED', 'CAD', 'BDT'].map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </Select>
              </Field>
            </div>
          </CardContent>
        </Card>

        <div className="flex gap-2">
          <Button type="submit" loading={save.isPending}>
            {isEdit ? 'Save changes' : 'Publish job'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/my-jobs')}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}
