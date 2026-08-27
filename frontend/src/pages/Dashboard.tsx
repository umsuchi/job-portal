import { Link } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { errorMessage } from '@/api/client'
import { suggestions } from '@/api/endpoints'
import { useAuth } from '@/context/AuthContext'
import { JobCard } from '@/components/JobCard'
import { Alert, Badge, Button, Card, EmptyState, Skeleton } from '@/components/ui'
import { timeAgo } from '@/lib/format'

export function DashboardPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const skills = user?.candidate_profile?.skills ?? []

  const { data, isPending, isFetching, error } = useQuery({
    queryKey: ['suggestions'],
    queryFn: () => suggestions.list(),
    staleTime: 5 * 60_000,
  })

  async function regenerate() {
    const fresh = await suggestions.list(true)
    queryClient.setQueryData(['suggestions'], fresh)
  }

  const firstName = user?.candidate_profile?.full_name?.split(' ')[0]

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {firstName ? `Recommended for you, ${firstName}` : 'Recommended for you'}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Ranked against the skills on your profile.
          </p>
        </div>

        {data ? (
          <div className="flex items-center gap-2">
            <Badge tone={data.source === 'ai' ? 'accent' : 'neutral'}>
              {data.source === 'ai' ? 'AI-ranked' : 'Skill-match ranking'}
            </Badge>
            <span className="text-xs text-muted-foreground">
              Updated {timeAgo(data.generated_at)}
            </span>
            <Button variant="outline" size="sm" loading={isFetching} onClick={regenerate}>
              Refresh
            </Button>
          </div>
        ) : null}
      </div>

      {error ? <Alert>{errorMessage(error, 'Could not load your recommendations.')}</Alert> : null}

      {isPending ? (
        <div className="space-y-3">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-40 w-full" />)}</div>
      ) : null}

      {data && skills.length === 0 ? (
        <EmptyState
          title="Add your skills to get recommendations"
          description="We match your skills against each job's requirements, then rank the results."
          action={<Link to="/profile"><Button>Add skills</Button></Link>}
        />
      ) : null}

      {data && skills.length > 0 && data.suggestions.length === 0 ? (
        <EmptyState
          title="Nothing matches your skills yet"
          description="No open role currently lists any of your skills. Browse everything, or widen your profile."
          action={<Link to="/jobs"><Button variant="outline">Browse all jobs</Button></Link>}
        />
      ) : null}

      <div className="space-y-3">
        {data?.suggestions.map((s) => (
          <div key={s.job.id} className="relative">
            <Card className="border-l-4 border-l-indigo-400 p-0">
              <div className="flex items-start gap-3 px-5 pt-4">
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-800">
                  {s.rank}
                </span>
                <p className="text-sm font-medium">{s.reason}</p>
              </div>
              <div className="p-1">
                <JobCard job={s.job} matched={s.matched_skills} />
              </div>
            </Card>
          </div>
        ))}
      </div>

      {data && data.suggestions.length > 0 ? (
        <p className="mt-6 text-center text-xs text-muted-foreground">
          {data.source === 'ai'
            ? 'Ranked and explained by an AI model, from jobs matching your skills.'
            : 'Ranked by how many of your skills each role requires.'}
        </p>
      ) : null}
    </div>
  )
}
