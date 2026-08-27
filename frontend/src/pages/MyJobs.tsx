import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { jobs } from '@/api/endpoints'
import { Badge, Button, Card, EmptyState, Skeleton } from '@/components/ui'
import { JOB_TYPE_LABELS, timeAgo } from '@/lib/format'

export function MyJobsPage() {
  const queryClient = useQueryClient()

  const { data, isPending } = useQuery({
    queryKey: ['jobs', 'mine'],
    queryFn: () => jobs.list({ mine: true, include_closed: true, limit: 100 }),
  })

  const close = useMutation({
    mutationFn: (id: string) => jobs.close(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['jobs'] }),
  })

  const reopen = useMutation({
    mutationFn: (id: string) => jobs.update(id, { status: 'open' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['jobs'] }),
  })

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Your job posts</h1>
          <p className="mt-1 text-sm text-muted-foreground">Post roles and review who applied.</p>
        </div>
        <Link to="/my-jobs/new"><Button>Post a job</Button></Link>
      </div>

      {isPending ? (
        <div className="space-y-3">{[0, 1].map((i) => <Skeleton key={i} className="h-28 w-full" />)}</div>
      ) : null}

      {data && data.items.length === 0 ? (
        <EmptyState
          title="No job posts yet"
          description="Your first post takes about a minute."
          action={<Link to="/my-jobs/new"><Button>Post a job</Button></Link>}
        />
      ) : null}

      <div className="space-y-3">
        {data?.items.map((job) => (
          <Card key={job.id} className="flex flex-wrap items-center justify-between gap-4 p-5">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <Link to={`/jobs/${job.id}`} className="font-semibold hover:underline">{job.title}</Link>
                <Badge tone={job.status === 'open' ? 'success' : 'neutral'}>
                  {job.status === 'open' ? 'Open' : 'Closed'}
                </Badge>
                <Badge>{JOB_TYPE_LABELS[job.job_type] ?? job.job_type}</Badge>
              </div>
              <p className="mt-1 text-sm text-muted-foreground">
                {job.location} · Posted {timeAgo(job.created_at)} ·{' '}
                {job.application_count ?? 0} applicant{job.application_count === 1 ? '' : 's'}
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              <Link to={`/my-jobs/${job.id}/applicants`}>
                <Button variant="secondary" size="sm">Applicants</Button>
              </Link>
              <Link to={`/my-jobs/${job.id}/edit`}>
                <Button variant="outline" size="sm">Edit</Button>
              </Link>
              {job.status === 'open' ? (
                <Button
                  variant="outline" size="sm"
                  loading={close.isPending && close.variables === job.id}
                  onClick={() => close.mutate(job.id)}
                >
                  Close
                </Button>
              ) : (
                <Button
                  variant="outline" size="sm"
                  loading={reopen.isPending && reopen.variables === job.id}
                  onClick={() => reopen.mutate(job.id)}
                >
                  Reopen
                </Button>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
