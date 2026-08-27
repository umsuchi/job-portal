import * as React from 'react'
import { useSearchParams } from 'react-router-dom'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { jobs } from '@/api/endpoints'
import { JobCard } from '@/components/JobCard'
import { SkillFilterInput } from '@/components/SkillInput'
import { Button, Card, EmptyState, Input, Select, Skeleton } from '@/components/ui'
import { JOB_TYPE_LABELS } from '@/lib/format'

const PAGE_SIZE = 10

export function JobsPage() {
  const [params, setParams] = useSearchParams()

  const q = params.get('q') ?? ''
  const skill = params.get('skill') ?? ''
  const location = params.get('location') ?? ''
  const jobType = params.get('job_type') ?? ''
  const page = Number(params.get('page') ?? '1')

  // Local mirror so typing does not re-run the query on every keystroke.
  const [draft, setDraft] = React.useState({ q, skill, location, jobType })

  const filters = React.useMemo(
    () => ({
      q: q || undefined,
      skill: skill ? [skill] : undefined,
      location: location || undefined,
      job_type: (jobType || undefined) as never,
      limit: PAGE_SIZE,
      offset: (page - 1) * PAGE_SIZE,
    }),
    [q, skill, location, jobType, page],
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
    setParams(next)
  }

  function clearFilters() {
    setDraft({ q: '', skill: '', location: '', jobType: '' })
    setParams(new URLSearchParams())
  }

  const total = data?.total ?? 0
  const lastPage = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const hasFilters = Boolean(q || skill || location || jobType)

  return (
    <div>
      <h1 className="mb-1 text-2xl font-semibold tracking-tight">Open roles</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        {isPending ? 'Loading…' : `${total} open ${total === 1 ? 'role' : 'roles'}`}
      </p>

      <Card className="mb-6 p-4">
        <form onSubmit={applyFilters} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
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
          <div className="flex gap-2">
            <Button type="submit" className="flex-1">Search</Button>
            {hasFilters ? (
              <Button type="button" variant="outline" onClick={clearFilters}>Clear</Button>
            ) : null}
          </div>
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
