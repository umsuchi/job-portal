import { Link } from 'react-router-dom'
import { Avatar } from '@/components/Avatar'
import { cn } from '@/lib/cn'
import { Badge, Card } from '@/components/ui'
import {
  DEADLINE_TONE, EXPERIENCE_LABELS, JOB_TYPE_LABELS, WORK_MODE_LABELS,
  deadlineState, formatSalary, timeAgo,
} from '@/lib/format'
import type { Job } from '@/api/types'

export function JobCard({
  job, matched, matchedNiceToHave,
}: {
  job: Job
  matched?: string[]
  matchedNiceToHave?: string[]
}) {
  const salary = formatSalary(job.salary_min, job.salary_max, job.salary_currency)
  const matchedSet = new Set((matched ?? []).map((s) => s.toLowerCase()))
  const niceSet = new Set((matchedNiceToHave ?? []).map((s) => s.toLowerCase()))
  const deadline = deadlineState(job.application_deadline, job.days_until_deadline)

  return (
    // `relative` anchors the stretched link below, so the whole card is a
    // click target while the accessibility tree still sees one link.
    <Card
      className={cn(
        'relative p-5 transition-shadow hover:shadow-md focus-within:ring-2 focus-within:ring-ring',
        // Expired posts stay readable but visibly inactive.
        job.is_expired ? 'opacity-70' : '',
      )}
    >
      <div className="flex items-start gap-3">
        <Avatar src={job.company?.avatar_url} name={job.company_name} size="lg" />

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div className="min-w-0">
              <Link
                to={`/jobs/${job.id}`}
                // The ::after overlay spans the whole card, so clicking anywhere
                // on it follows this link — without nesting a second anchor.
                className="text-base font-semibold after:absolute after:inset-0 after:rounded-lg hover:underline focus:outline-none"
              >
                {job.title}
              </Link>
              <p className="mt-0.5 text-sm text-muted-foreground">
                {job.company_name ?? 'Independent recruiter'} · {job.location}
              </p>
            </div>
            <div className="flex shrink-0 flex-wrap items-center gap-1.5">
              {job.is_expired ? <Badge tone="danger">Expired</Badge> : null}
              {!job.is_expired && deadline.tone === 'today'
                ? <Badge tone="danger">Closes today</Badge> : null}
              {!job.is_expired && deadline.tone === 'soon'
                ? <Badge tone="warn">{deadline.label}</Badge> : null}
              {job.has_applied ? <Badge tone="success">Applied</Badge> : null}
              <Badge tone={job.work_mode === 'remote' ? 'info' : 'neutral'}>
                {WORK_MODE_LABELS[job.work_mode] ?? job.work_mode}
              </Badge>
              <Badge>{JOB_TYPE_LABELS[job.job_type] ?? job.job_type}</Badge>
            </div>
          </div>

          <div className="mt-3 flex flex-wrap gap-1.5">
            {job.required_skills.map((skill) => (
              <Badge key={skill} tone={matchedSet.has(skill.toLowerCase()) ? 'success' : 'neutral'}>
                {skill}
              </Badge>
            ))}
            {job.nice_to_have_skills.slice(0, 3).map((skill) => (
              <Badge
                key={skill}
                tone={niceSet.has(skill.toLowerCase()) ? 'success' : 'neutral'}
                className="opacity-70"
                title="Nice to have"
              >
                {skill}
              </Badge>
            ))}
          </div>

          <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
            <span>{EXPERIENCE_LABELS[job.experience_level] ?? job.experience_level}</span>
            {job.min_years_experience ? <span>{job.min_years_experience}+ years</span> : null}
            {salary ? <span>{salary}</span> : null}
            <span>Posted {timeAgo(job.created_at)}</span>
            {deadline.tone === 'open' || deadline.tone === 'expired' ? (
              <span className={DEADLINE_TONE[deadline.tone] === 'danger' ? 'text-rose-700' : ''}>
                {deadline.label}
              </span>
            ) : null}
            {job.application_count != null ? (
              <span>
                {job.application_count} applicant{job.application_count === 1 ? '' : 's'}
              </span>
            ) : null}
          </div>
        </div>
      </div>
    </Card>
  )
}
