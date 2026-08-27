import * as React from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { errorMessage } from '@/api/client'
import { jobs } from '@/api/endpoints'
import { SkillInput } from '@/components/SkillInput'
import { Alert, Button, Card, Field, Input, Select, Skeleton, Textarea } from '@/components/ui'
import { JOB_TYPE_LABELS } from '@/lib/format'
import type { JobType } from '@/api/types'

interface FormState {
  title: string
  description: string
  required_skills: string[]
  location: string
  job_type: JobType
  salary_min: string
  salary_max: string
}

const EMPTY: FormState = {
  title: '', description: '', required_skills: [], location: '',
  job_type: 'full_time', salary_min: '', salary_max: '',
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
      required_skills: existing.required_skills,
      location: existing.location,
      job_type: existing.job_type,
      salary_min: existing.salary_min?.toString() ?? '',
      salary_max: existing.salary_max?.toString() ?? '',
    })
    setHydrated(true)
  }, [existing, hydrated])

  const save = useMutation({
    mutationFn: () => {
      const body = {
        title: form.title,
        description: form.description,
        required_skills: form.required_skills,
        location: form.location,
        job_type: form.job_type,
        salary_min: form.salary_min ? Number(form.salary_min) : null,
        salary_max: form.salary_max ? Number(form.salary_max) : null,
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
        Required skills are what candidates get matched against.
      </p>

      <Card className="p-6">
        <form
          className="space-y-5"
          onSubmit={(e) => { e.preventDefault(); setError(null); save.mutate() }}
        >
          {error ? <Alert>{error}</Alert> : null}

          <Field label="Title">
            <Input required minLength={2} value={form.title}
                   placeholder="Senior React Engineer"
                   onChange={(e) => set('title', e.target.value)} />
          </Field>

          <Field label="Description" hint="At least a couple of sentences.">
            <Textarea required minLength={10} className="min-h-[160px]" value={form.description}
                      placeholder="What the role involves, who you are looking for…"
                      onChange={(e) => set('description', e.target.value)} />
          </Field>

          <Field label="Required skills" hint="At least one. Press Enter after each.">
            <SkillInput
              value={form.required_skills}
              onChange={(next) => set('required_skills', next)}
              placeholder="React, TypeScript, PostgreSQL…"
            />
          </Field>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Location">
              <Input required value={form.location} placeholder="Remote / Berlin / Dhaka"
                     onChange={(e) => set('location', e.target.value)} />
            </Field>
            <Field label="Job type">
              <Select value={form.job_type}
                      onChange={(e) => set('job_type', e.target.value as JobType)}>
                {Object.entries(JOB_TYPE_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </Select>
            </Field>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Salary minimum" hint="Optional.">
              <Input type="number" min={0} value={form.salary_min}
                     onChange={(e) => set('salary_min', e.target.value)} />
            </Field>
            <Field label="Salary maximum" hint="Optional.">
              <Input type="number" min={0} value={form.salary_max}
                     onChange={(e) => set('salary_max', e.target.value)} />
            </Field>
          </div>

          <div className="flex gap-2">
            <Button type="submit" loading={save.isPending}>
              {isEdit ? 'Save changes' : 'Publish job'}
            </Button>
            <Button type="button" variant="outline" onClick={() => navigate('/my-jobs')}>
              Cancel
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
