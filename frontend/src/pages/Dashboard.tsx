import { Link } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { errorMessage } from '@/api/client'
import { suggestions } from '@/api/endpoints'
import { useAuth } from '@/context/AuthContext'
import { JobCard } from '@/components/JobCard'
import { Alert, Badge, Button, Card, EmptyState, Skeleton } from '@/components/ui'
import { timeAgo } from '@/lib/format'

/** Preferences the candidate has not filled in, in priority order. */
function missingInputs(profile: {
  years_experience: number | null
  preferred_work_modes: string[]
  preferred_locations: string[]
  desired_salary_min: number | null
} | null | undefined): string[] {
  if (!profile) return []
  const gaps: string[] = []
  if (profile.years_experience == null) gaps.push('years of experience')
  if (!profile.preferred_work_modes.length) gaps.push('preferred work arrangement')
  if (!profile.preferred_locations.length) gaps.push('preferred locations')
  if (profile.desired_salary_min == null) gaps.push('minimum salary')
  return gaps
}

export function DashboardPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const profile = user?.candidate_profile
  const skills = profile?.skills ?? []

  const { data, isPending, isFetching, error } = useQuery({
    queryKey: ['suggestions'],
    queryFn: () => suggestions.list(),
    staleTime: 5 * 60_000,
  })

  async function regenerate() {
    const fresh = await suggestions.list(true)
    queryClient.setQueryData(['suggestions'], fresh)
  }

  const firstName = profile?.full_name?.split(' ')[0]
  const gaps = missingInputs(profile)

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {firstName ? `Recommended for you, ${firstName}` : 'Recommended for you'}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Ranked on your skills, seniority and what you told us you are looking for.
          </p>
        </div>

        {data ? (
          <div className="flex items-center gap-2">
            <Badge tone={data.source === 'ai' ? 'accent' : 'neutral'}>
              {data.source === 'ai' ? 'AI-ranked' : 'Profile-match ranking'}
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
        <div className="space-y-3">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-44 w-full" />)}</div>
      ) : null}

      {data && skills.length === 0 ? (
        <EmptyState
          title="Add your skills to get recommendations"
          description="We match your skills against each job's requirements, then rank the results on your experience and preferences."
          action={<Link to="/profile"><Button>Complete your profile</Button></Link>}
        />
      ) : null}

      {data && skills.length > 0 && data.suggestions.length === 0 ? (
        <EmptyState
          title="Nothing matches your skills yet"
          description="No open role currently lists any of your skills. Browse everything, or widen your profile."
          action={<Link to="/jobs"><Button variant="outline">Browse all jobs</Button></Link>}
        />
      ) : null}

      {data && data.suggestions.length > 0 && gaps.length > 0 ? (
        <Card className="mb-4 border-dashed p-4">
          <p className="text-sm">
            <span className="font-medium">These rankings could be sharper.</span>{' '}
            You have not set your {gaps.slice(0, 2).join(' or ')}
            {gaps.length > 2 ? `, among others` : ''} — so we cannot weigh{' '}
            {gaps.length > 1 ? 'those' : 'that'} yet.{' '}
            <Link to="/profile" className="font-medium underline">Fill them in</Link>.
          </p>
        </Card>
      ) : null}

      <div className="space-y-3">
        {data?.suggestions.map((s) => (
          <Card key={s.job.id} className="border-l-4 border-l-indigo-400 p-0">
            <div className="flex items-start gap-3 px-5 pt-4">
              <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-800">
                {s.rank}
              </span>
              <div className="min-w-0">
                <p className="text-sm font-medium">{s.reason}</p>
                {s.signals.length > 0 ? (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {s.signals.map((signal) => (
                      <Badge key={signal} tone="info" className="font-normal">{signal}</Badge>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
            <div className="p-1">
              <JobCard
                job={s.job}
                matched={s.matched_skills}
                matchedNiceToHave={s.matched_nice_to_have}
              />
            </div>
          </Card>
        ))}
      </div>

      {data && data.suggestions.length > 0 ? (
        <p className="mt-6 text-center text-xs text-muted-foreground">
          {data.source === 'ai'
            ? 'Ranked and explained by an AI model, from jobs matching your profile.'
            : 'Ranked on skill overlap, seniority fit, work arrangement, location and salary.'}
        </p>
      ) : null}
    </div>
  )
}
