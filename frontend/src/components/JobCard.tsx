import { Link } from 'react-router-dom'
import { Badge, Card } from '@/components/ui'
import { JOB_TYPE_LABELS, formatSalary, timeAgo } from '@/lib/format'
import type { Job } from '@/api/types'

export function JobCard({ job, matched }: { job: Job; matched?: string[] }) {
  const salary = formatSalary(job.salary_min, job.salary_max)
  const matchedSet = new Set((matched ?? []).map((s) => s.toLowerCase()))

  return (
    <Card className="p-5 transition-shadow hover:shadow-md">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
          <Link to={`/jobs/${job.id}`} className="text-base font-semibold hover:underline">
            {job.title}
          </Link>
          <p className="mt-0.5 text-sm text-muted-foreground">
            {job.company_name ?? 'Independent recruiter'} · {job.location}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {job.has_applied ? <Badge tone="success">Applied</Badge> : null}
          <Badge>{JOB_TYPE_LABELS[job.job_type] ?? job.job_type}</Badge>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-1.5">
        {job.required_skills.map((skill) => (
          <Badge key={skill} tone={matchedSet.has(skill.toLowerCase()) ? 'success' : 'neutral'}>
            {skill}
          </Badge>
        ))}
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
        {salary ? <span>{salary}</span> : null}
        <span>Posted {timeAgo(job.created_at)}</span>
        {job.application_count != null ? (
          <span>
            {job.application_count} applicant{job.application_count === 1 ? '' : 's'}
          </span>
        ) : null}
      </div>
    </Card>
  )
}
