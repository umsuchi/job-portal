import * as React from 'react'
import { useSearchParams } from 'react-router-dom'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { jobs } from '@/api/endpoints'
import { JobCard } from '@/components/JobCard'
import { SkillFilterInput } from '@/components/SkillInput'
import { Button, Card, EmptyState, Input, Select, Skeleton } from '@/components/ui'
import { EXPERIENCE_LABELS, JOB_TYPE_LABELS, WORK_MODE_LABELS } from '@/lib/format'

const PAGE_SIZE = 10

export function JobsPage() {
  const [params, setParams] = useSearchParams()

  const q = params.get('q') ?? ''
  const skill = params.get('skill') ?? ''
  const location = params.get('location') ?? ''
  const jobType = params.get('job_type') ?? ''
  const workMode = params.get('work_mode') ?? ''
  const experienceLevel = params.get('experience_level') ?? ''
  const includeExpired = params.get('include_expired') === '1'
  const page = Number(params.get('page') ?? '1')

  // Local mirror so typing does not re-run the query on every keystroke.
  const [draft, setDraft] = React.useState({
    q, skill, location, jobType, workMode, experienceLevel,
  })

  const filters = React.useMemo(
    () => ({
      q: q || undefined,
      skill: skill ? [skill] : undefined,
      location: location || undefined,
      job_type: (jobType || undefined) as never,
      work_mode: (workMode || undefined) as never,
      experience_level: (experienceLevel || undefined) as never,
      include_expired: includeExpired || undefined,
      limit: PAGE_SIZE,
      offset: (page - 1) * PAGE_SIZE,
    }),
    [q, skill, location, jobType, workMode, experienceLevel, includeExpired, page],
  )

  const { data, isPending, isError } = useQuery({
    queryKey: ['jobs', filters],
    queryFn: () => jobs.list(filters),
    placeholderData: keepPreviousData,
  })

  function applyFilters(e: React.FormEvent) {
    e.preventDefault()
    const next = new URLSearchParams()
    if (draft.q) next.set('q', draft.q)
    if (draft.skill) next.set('skill', draft.skill)
    if (draft.location) next.set('location', draft.location)
    if (draft.jobType) next.set('job_type', draft.jobType)
    if (draft.workMode) next.set('work_mode', draft.workMode)
    if (draft.experienceLevel) next.set('experience_level', draft.experienceLevel)
    if (includeExpired) next.set('include_expired', '1')
    setParams(next)
  }

  function clearFilters() {
    setDraft({ q: '', skill: '', location: '', jobType: '', workMode: '', experienceLevel: '' })
    setParams(new URLSearchParams())
  }

  const total = data?.total ?? 0
  const lastPage = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const hasFilters = Boolean(q || skill || location || jobType || workMode || experienceLevel)

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold tracking-tight">Open roles</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        {isPending ? 'Loading…' : `${total} open ${total === 1 ? 'role' : 'roles'}`}
      </p>

      <Card className="mb-6 p-4">
        <form onSubmit={applyFilters} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Input
            placeholder="Keyword"
            value={draft.q}
            onChange={(e) => setDraft((d) => ({ ...d, q: e.target.value }))}
          />
          <SkillFilterInput
            value={draft.skill}
            onChange={(skill) => setDraft((d) => ({ ...d, skill }))}
          />
          <Input
            placeholder="Location"
            value={draft.location}
            onChange={(e) => setDraft((d) => ({ ...d, location: e.target.value }))}
          />
          <Select
            value={draft.jobType}
            onChange={(e) => setDraft((d) => ({ ...d, jobType: e.target.value }))}
          >
            <option value="">Any type</option>
            {Object.entries(JOB_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </Select>
          <Select
            value={draft.workMode}
            onChange={(e) => setDraft((d) => ({ ...d, workMode: e.target.value }))}
          >
            <option value="">Anywhere</option>
            {Object.entries(WORK_MODE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </Select>
          <Select
            value={draft.experienceLevel}
            onChange={(e) => setDraft((d) => ({ ...d, experienceLevel: e.target.value }))}
          >
            <option value="">Any level</option>
            {Object.entries(EXPERIENCE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </Select>
          <div className="flex gap-2">
            <Button type="submit" className="flex-1">Search</Button>
            {hasFilters ? (
              <Button type="button" variant="outline" onClick={clearFilters}>Clear</Button>
            ) : null}
          </div>

          <label className="flex items-center gap-2 text-sm text-muted-foreground sm:col-span-2 lg:col-span-4">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-input"
              checked={includeExpired}
              onChange={(e) => {
                // Applies immediately — it changes what is listed, not how it is searched.
                setParams((p) => {
                  if (e.target.checked) p.set('include_expired', '1')
                  else p.delete('include_expired')
                  return p
                })
              }}
            />
            Include roles past their application deadline
          </label>
        </form>
      </Card>

      {isError ? (
        <EmptyState
          title="Could not load jobs"
          description="The API did not respond. Check that the backend is running, then try again."
        />
      ) : null}

      {isPending ? (
        <div className="space-y-3">
          {[0, 1, 2].map((i) => <Skeleton key={i} className="h-36 w-full" />)}
        </div>
      ) : null}

      {data && data.items.length === 0 ? (
        <EmptyState
          title="No roles match those filters"
          description={hasFilters ? 'Try widening your search.' : 'Check back soon — new roles appear here.'}
          action={hasFilters ? <Button variant="outline" onClick={clearFilters}>Clear filters</Button> : undefined}
        />
      ) : null}

      <div className="space-y-3">
        {data?.items.map((job) => <JobCard key={job.id} job={job} />)}
      </div>

      {lastPage > 1 ? (
        <div className="mt-6 flex items-center justify-center gap-3">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setParams((p) => { p.set('page', String(page - 1)); return p })}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">Page {page} of {lastPage}</span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= lastPage}
            onClick={() => setParams((p) => { p.set('page', String(page + 1)); return p })}
          >
            Next
          </Button>
        </div>
      ) : null}
    </div>
  )
}
