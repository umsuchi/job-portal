import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { errorMessage } from '@/api/client'
import { applications } from '@/api/endpoints'
import { Alert, Badge, Button, Card, EmptyState, Skeleton } from '@/components/ui'
import { Avatar } from '@/components/Avatar'
import { STATUS_LABELS, STATUS_TONE, WORK_MODE_LABELS, timeAgo } from '@/lib/format'

const TERMINAL = new Set(['hired', 'rejected', 'withdrawn'])

export function MyApplicationsPage() {
  const queryClient = useQueryClient()

  const { data, isPending, error } = useQuery({
    queryKey: ['my-applications'],
    queryFn: applications.mine,
    refetchInterval: 30_000,
  })

  const withdraw = useMutation({
    mutationFn: (id: string) => applications.withdraw(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['my-applications'] }),
  })

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-1 text-2xl font-semibold tracking-tight">Your applications</h1>
      <p className="mb-6 text-sm text-muted-foreground">Most recent first.</p>

      {error ? <Alert>{errorMessage(error, 'Could not load your applications.')}</Alert> : null}
      {isPending ? (
        <div className="space-y-3">{[0, 1].map((i) => <Skeleton key={i} className="h-28 w-full" />)}</div>
      ) : null}

      {data && data.length === 0 ? (
        <EmptyState
          title="You have not applied to anything yet"
          description="Browse open roles, or see what we recommend for your skills."
          action={<Link to="/dashboard"><Button>See recommendations</Button></Link>}
        />
      ) : null}

      <div className="space-y-3">
        {data?.map((a) => (
          <Card key={a.id} className="flex flex-wrap items-center justify-between gap-4 p-5">
            <div className="flex min-w-0 items-start gap-3">
              <Avatar src={a.job?.company_avatar_url} name={a.job?.company_name} />
              <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <Link to={`/jobs/${a.job_id}`} className="font-semibold hover:underline">
                  {a.job?.title ?? 'Job'}
                </Link>
                <Badge tone={STATUS_TONE[a.status]}>{STATUS_LABELS[a.status]}</Badge>
                {a.unread_messages > 0 ? <Badge tone="accent">{a.unread_messages} new</Badge> : null}
                {a.job?.is_expired ? <Badge tone="neutral">Post expired</Badge> : null}
              </div>
              <p className="mt-1 text-sm text-muted-foreground">
                {a.job?.company_name ?? 'Independent recruiter'} · {a.job?.location}
                {a.job ? ` · ${WORK_MODE_LABELS[a.job.work_mode] ?? a.job.work_mode}` : ''} ·
                {' '}Applied {timeAgo(a.applied_at)}
              </p>
              </div>
            </div>

            <div className="flex gap-2">
              <Link to={`/applications/${a.id}/messages`}>
                <Button variant="secondary" size="sm">Messages</Button>
              </Link>
              {TERMINAL.has(a.status) ? null : (
                <Button
                  variant="outline" size="sm"
                  loading={withdraw.isPending && withdraw.variables === a.id}
                  onClick={() => withdraw.mutate(a.id)}
                >
                  Withdraw
                </Button>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
