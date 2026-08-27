import * as React from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { errorMessage } from '@/api/client'
import { applications, jobs } from '@/api/endpoints'
import { useAuth } from '@/context/AuthContext'
import { Avatar } from '@/components/Avatar'
import {
  Alert, Badge, Button, Card, CardContent, CardHeader, CardTitle, Dialog, EmptyState,
  Skeleton, Textarea,
} from '@/components/ui'
import {
  EXPERIENCE_LABELS, JOB_TYPE_LABELS, WORK_MODE_LABELS,
  deadlineState, formatSalary, timeAgo,
} from '@/lib/format'

function BulletSection({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null
  return (
    <Card>
      <CardHeader><CardTitle>{title}</CardTitle></CardHeader>
      <CardContent>
        <ul className="space-y-2 text-sm leading-relaxed">
          {items.map((item) => (
            <li key={item} className="flex gap-2.5">
              <span aria-hidden className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-muted-foreground" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

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

  const salary = formatSalary(job.salary_min, job.salary_max, job.salary_currency)
  const isOwner = user?.id === job.recruiter_id
  const deadline = deadlineState(job.application_deadline, job.days_until_deadline)
  // `accepts_applications` is the server's own answer — open AND not expired.
  const canApply =
    user?.role === 'candidate' && job.accepts_applications && !job.has_applied

  const facts: Array<[string, string | null]> = [
    ['Location', job.location],
    ['Work arrangement', WORK_MODE_LABELS[job.work_mode] ?? job.work_mode],
    ['Employment type', JOB_TYPE_LABELS[job.job_type] ?? job.job_type],
    ['Experience', EXPERIENCE_LABELS[job.experience_level] ?? job.experience_level],
    ['Minimum years', job.min_years_experience ? `${job.min_years_experience}+` : null],
    ['Salary', salary],
    ['Application deadline', deadline.date],
  ]

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <Link to="/jobs" className="text-sm text-muted-foreground hover:underline">← All jobs</Link>

      <Card className="p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex items-start gap-4">
            <Avatar src={job.company?.avatar_url} name={job.company_name} size="lg" />
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">{job.title}</h1>
              <p className="mt-1 text-sm text-muted-foreground">
                {job.company_name ?? 'Independent recruiter'}
                {job.company?.industry ? ` · ${job.company.industry}` : ''}
                {' · '}Posted {timeAgo(job.created_at)}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {job.status === 'closed' ? <Badge tone="danger">Closed</Badge> : null}
            {job.is_expired ? <Badge tone="danger">Expired</Badge> : null}
            {!job.is_expired && deadline.tone === 'today'
              ? <Badge tone="danger">Closes today</Badge> : null}
            {!job.is_expired && deadline.tone === 'soon'
              ? <Badge tone="warn">{deadline.label}</Badge> : null}
            <Badge tone={job.work_mode === 'remote' ? 'info' : 'neutral'}>
              {WORK_MODE_LABELS[job.work_mode] ?? job.work_mode}
            </Badge>
            <Badge>{JOB_TYPE_LABELS[job.job_type] ?? job.job_type}</Badge>
          </div>
        </div>

        <dl className="mt-6 grid grid-cols-2 gap-x-6 gap-y-3 border-y border-border py-4 sm:grid-cols-3">
          {facts.filter(([, v]) => v).map(([label, value]) => (
            <div key={label}>
              <dt className="text-xs uppercase tracking-wide text-muted-foreground">{label}</dt>
              <dd className="mt-0.5 text-sm font-medium">{value}</dd>
            </div>
          ))}
        </dl>

        <div className="mt-5">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Required skills</p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {job.required_skills.map((s) => <Badge key={s} tone="accent">{s}</Badge>)}
          </div>
        </div>

        {job.nice_to_have_skills.length > 0 ? (
          <div className="mt-4">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Nice to have</p>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {job.nice_to_have_skills.map((s) => <Badge key={s}>{s}</Badge>)}
            </div>
          </div>
        ) : null}

        <div className="mt-6 whitespace-pre-wrap text-sm leading-relaxed">
          {job.description}
        </div>

        {job.is_expired ? (
          <div className="mt-6">
            <Alert>
              <span className="font-medium">Applications have closed.</span>{' '}
              The deadline for this role was {deadline.date}.
            </Alert>
          </div>
        ) : null}

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
          {user?.role === 'recruiter' && !isOwner ? (
            // Otherwise this row is simply empty and looks broken.
            <p className="self-center text-sm text-muted-foreground">
              You are signed in as a recruiter — only candidates can apply.
            </p>
          ) : null}
          {user?.role === 'candidate' && job.status === 'closed' && !job.has_applied ? (
            <p className="self-center text-sm text-muted-foreground">
              This role is closed and no longer accepting applications.
            </p>
          ) : null}
          {isOwner && job.is_expired ? (
            <p className="self-center text-sm text-muted-foreground">
              Extend the deadline to start accepting applications again.
            </p>
          ) : null}
        </div>
      </Card>

      <BulletSection title="What you will do" items={job.responsibilities} />
      <BulletSection title="What we are looking for" items={job.requirements} />
      <BulletSection title="What we offer" items={job.benefits} />

      {job.company?.about ? (
        <Card>
          <CardHeader><CardTitle>About {job.company.name}</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <p className="whitespace-pre-wrap text-sm leading-relaxed">{job.company.about}</p>
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
              {job.company.headquarters ? <span>{job.company.headquarters}</span> : null}
              {job.company.website ? (
                <a
                  href={job.company.website} target="_blank" rel="noreferrer"
                  className="hover:underline"
                >
                  {job.company.website.replace(/^https?:\/\//, '')}
                </a>
              ) : null}
            </div>
          </CardContent>
        </Card>
      ) : null}

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
