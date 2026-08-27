import * as React from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { errorMessage } from '@/api/client'
import { applications, jobs } from '@/api/endpoints'
import { useAuth } from '@/context/AuthContext'
import { Alert, Badge, Button, Card, Dialog, EmptyState, Skeleton, Textarea } from '@/components/ui'
import { JOB_TYPE_LABELS, formatSalary, timeAgo } from '@/lib/format'

export function JobDetailPage() {
  const { jobId = '' } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [open, setOpen] = React.useState(false)
  const [coverNote, setCoverNote] = React.useState('')
  const [error, setError] = React.useState<string | null>(null)

  const { data: job, isPending, isError } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobs.get(jobId),
  })

  const apply = useMutation({
    mutationFn: () => applications.apply({ job_id: jobId, cover_note: coverNote || undefined }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job', jobId] })
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['my-applications'] })
      setOpen(false)
      navigate('/applications')
    },
    onError: (err) => setError(errorMessage(err, 'Could not submit your application.')),
  })

  if (isPending) return <Skeleton className="h-72 w-full" />
  if (isError || !job) {
    return (
      <EmptyState
        title="Job not found"
        description="It may have been closed by the recruiter."
        action={<Link to="/jobs"><Button variant="outline">Back to jobs</Button></Link>}
      />
    )
  }

  const salary = formatSalary(job.salary_min, job.salary_max)
  const isOwner = user?.id === job.recruiter_id
  const canApply = user?.role === 'candidate' && job.status === 'open' && !job.has_applied

  return (
    <div className="mx-auto max-w-3xl">
      <Link to="/jobs" className="text-sm text-muted-foreground hover:underline">← All jobs</Link>

      <Card className="mt-4 p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">{job.title}</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {job.company_name ?? 'Independent recruiter'} · {job.location} · Posted {timeAgo(job.created_at)}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {job.status === 'closed' ? <Badge tone="danger">Closed</Badge> : null}
            <Badge>{JOB_TYPE_LABELS[job.job_type] ?? job.job_type}</Badge>
          </div>
        </div>

        {salary ? <p className="mt-3 text-sm font-medium">{salary}</p> : null}

        <div className="mt-4 flex flex-wrap gap-1.5">
          {job.required_skills.map((s) => <Badge key={s} tone="accent">{s}</Badge>)}
        </div>

        <div className="prose-sm mt-6 whitespace-pre-wrap text-sm leading-relaxed">
          {job.description}
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          {canApply ? <Button onClick={() => setOpen(true)}>Apply for this role</Button> : null}
          {job.has_applied ? (
            <Link to="/applications">
              <Button variant="outline">You have applied — view application</Button>
            </Link>
          ) : null}
          {isOwner ? (
            <>
              <Link to={`/my-jobs/${job.id}/edit`}><Button variant="outline">Edit post</Button></Link>
              <Link to={`/my-jobs/${job.id}/applicants`}>
                <Button variant="secondary">
                  View {job.application_count ?? 0} applicant{job.application_count === 1 ? '' : 's'}
                </Button>
              </Link>
            </>
          ) : null}
          {!user ? (
            <Link to="/login"><Button variant="outline">Sign in to apply</Button></Link>
          ) : null}
        </div>
      </Card>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        title={`Apply — ${job.title}`}
        description="Add a short note for the recruiter. Optional, but it helps."
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
            <Button loading={apply.isPending} onClick={() => { setError(null); apply.mutate() }}>
              Submit application
            </Button>
          </>
        }
      >
        {error ? <div className="mb-3"><Alert>{error}</Alert></div> : null}
        <Textarea
          maxLength={4000}
          placeholder="Why you are a good fit…"
          value={coverNote}
          onChange={(e) => setCoverNote(e.target.value)}
        />
      </Dialog>
    </div>
  )
}
