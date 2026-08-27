import { Link, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { errorMessage } from '@/api/client'
import { applications, jobs } from '@/api/endpoints'
import { Alert, Badge, Button, Card, EmptyState, Select, Skeleton } from '@/components/ui'
import { Avatar } from '@/components/Avatar'
import { EXPERIENCE_LABELS, STATUS_LABELS, STATUS_TONE, timeAgo } from '@/lib/format'
import type { ApplicationStatus } from '@/api/types'

/** Legal next states per the lifecycle in spec §11.2 — mirrored here so the UI
 *  only ever offers transitions the API will accept. */
const NEXT_STATES: Record<string, ApplicationStatus[]> = {
  applied: ['reviewed', 'rejected'],
  reviewed: ['shortlisted', 'rejected'],
  shortlisted: ['hired', 'rejected'],
  rejected: [],
  hired: [],
  withdrawn: [],
}

export function ApplicantsPage() {
  const { jobId = '' } = useParams()
  const queryClient = useQueryClient()

  const { data: job } = useQuery({ queryKey: ['job', jobId], queryFn: () => jobs.get(jobId) })
  const { data, isPending, error } = useQuery({
    queryKey: ['applicants', jobId],
    queryFn: () => jobs.applicants(jobId),
  })

  const setStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: ApplicationStatus }) =>
      applications.setStatus(id, status as never),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applicants', jobId] })
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })

  return (
    <div className="mx-auto max-w-4xl">
      <Link to="/my-jobs" className="text-sm text-muted-foreground hover:underline">← Your job posts</Link>

      <h1 className="mt-4 text-2xl font-semibold tracking-tight">
        {job ? `Applicants — ${job.title}` : 'Applicants'}
      </h1>
      <p className="mb-6 mt-1 text-sm text-muted-foreground">
        {data ? `${data.length} application${data.length === 1 ? '' : 's'}` : 'Loading…'}
      </p>

      {error ? <Alert>{errorMessage(error, 'Could not load applicants.')}</Alert> : null}
      {isPending ? (
        <div className="space-y-3">{[0, 1].map((i) => <Skeleton key={i} className="h-32 w-full" />)}</div>
      ) : null}

      {data && data.length === 0 ? (
        <EmptyState
          title="No applications yet"
          description="They will appear here as candidates apply."
        />
      ) : null}

      <div className="space-y-3">
        {data?.map((a) => {
          const options = NEXT_STATES[a.status] ?? []
          return (
            <Card key={a.id} className="p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="flex min-w-0 items-start gap-3">
                  <Avatar
                    src={a.candidate.avatar_url}
                    name={a.candidate.full_name ?? a.candidate.email}
                    size="lg"
                  />
                  <div className="min-w-0">
                    <p className="font-semibold">{a.candidate.full_name ?? a.candidate.email}</p>
                    <p className="text-sm text-muted-foreground">
                      {a.candidate.headline ?? a.candidate.email}
                    </p>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      {[
                        a.candidate.experience_level
                          ? EXPERIENCE_LABELS[a.candidate.experience_level]
                          : null,
                        a.candidate.years_experience != null
                          ? `${a.candidate.years_experience} yrs`
                          : null,
                        a.candidate.location,
                        `Applied ${timeAgo(a.applied_at)}`,
                      ].filter(Boolean).join(' · ')}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {a.unread_messages > 0 ? <Badge tone="accent">{a.unread_messages} new</Badge> : null}
                  <Badge tone={STATUS_TONE[a.status]}>{STATUS_LABELS[a.status]}</Badge>
                </div>
              </div>

              {a.candidate.bio ? (
                <p className="mt-3 line-clamp-3 text-sm text-muted-foreground">
                  {a.candidate.bio}
                </p>
              ) : null}

              {a.candidate.skills.length > 0 ? (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {a.candidate.skills.map((s) => <Badge key={s}>{s}</Badge>)}
                </div>
              ) : null}

              {a.cover_note ? (
                <p className="mt-3 whitespace-pre-wrap rounded-md bg-muted/60 p-3 text-sm">
                  {a.cover_note}
                </p>
              ) : null}

              <div className="mt-4 flex flex-wrap items-center gap-2">
                <Link to={`/applications/${a.id}/messages`}>
                  <Button variant="secondary" size="sm">Message</Button>
                </Link>

                {a.candidate.resume_url ? (
                  <a href={a.candidate.resume_url} target="_blank" rel="noreferrer">
                    <Button variant="outline" size="sm">Resume</Button>
                  </a>
                ) : null}

                {options.length > 0 ? (
                  <Select
                    className="h-8 w-auto text-xs"
                    value=""
                    disabled={setStatus.isPending}
                    onChange={(e) => {
                      const status = e.target.value as ApplicationStatus
                      if (status) setStatus.mutate({ id: a.id, status })
                    }}
                  >
                    <option value="">Move to…</option>
                    {options.map((s) => (
                      <option key={s} value={s}>{STATUS_LABELS[s]}</option>
                    ))}
                  </Select>
                ) : (
                  <span className="text-xs text-muted-foreground">
                    {a.status === 'withdrawn' ? 'Candidate withdrew.' : 'This application is closed.'}
                  </span>
                )}
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
