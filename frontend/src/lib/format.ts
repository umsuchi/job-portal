export const JOB_TYPE_LABELS: Record<string, string> = {
  full_time: 'Full-time',
  part_time: 'Part-time',
  contract: 'Contract',
  internship: 'Internship',
  temporary: 'Temporary',
}

export const WORK_MODE_LABELS: Record<string, string> = {
  onsite: 'On-site',
  hybrid: 'Hybrid',
  remote: 'Remote',
}

export const EXPERIENCE_LABELS: Record<string, string> = {
  entry: 'Entry level',
  junior: 'Junior',
  mid: 'Mid level',
  senior: 'Senior',
  lead: 'Lead',
  principal: 'Principal',
}

export const STATUS_LABELS: Record<string, string> = {
  applied: 'Applied',
  reviewed: 'Reviewed',
  shortlisted: 'Shortlisted',
  rejected: 'Rejected',
  hired: 'Hired',
  withdrawn: 'Withdrawn',
}

export const STATUS_TONE: Record<string, 'neutral' | 'info' | 'success' | 'danger' | 'warn'> = {
  applied: 'neutral',
  reviewed: 'info',
  shortlisted: 'warn',
  rejected: 'danger',
  hired: 'success',
  withdrawn: 'neutral',
}

const CURRENCY_SYMBOLS: Record<string, string> = { USD: '$', EUR: '€', GBP: '£' }

export function formatSalary(
  min?: number | null, max?: number | null, currency = 'USD',
): string | null {
  const symbol = CURRENCY_SYMBOLS[currency] ?? `${currency} `
  const fmt = (n: number) => (n >= 1000 ? `${Math.round(n / 1000)}k` : `${n}`)
  if (min != null && max != null) return `${symbol}${fmt(min)} – ${symbol}${fmt(max)}`
  if (min != null) return `From ${symbol}${fmt(min)}`
  if (max != null) return `Up to ${symbol}${fmt(max)}`
  return null
}

export function formatExperience(level?: string | null, minYears?: number | null): string | null {
  const parts = [level ? EXPERIENCE_LABELS[level] ?? level : null,
                 minYears ? `${minYears}+ yrs` : null].filter(Boolean)
  return parts.length ? parts.join(' · ') : null
}

export function timeAgo(iso: string): string {
  const then = new Date(iso).getTime()
  const secs = Math.max(1, Math.floor((Date.now() - then) / 1000))
  if (secs < 60) return 'just now'
  const mins = Math.floor(secs / 60)
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}d ago`
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

/** How close a deadline has to be before we call it urgent. Matches the backend. */
export const CLOSING_SOON_DAYS = 7

export type DeadlineTone = 'expired' | 'today' | 'soon' | 'open' | 'none'

export interface DeadlineState {
  tone: DeadlineTone
  /** Short label for a badge, e.g. "Closes in 3 days". */
  label: string
  /** Full date, for the detail page. */
  date: string | null
}

/**
 * Turn the server's derived deadline fields into something displayable.
 *
 * `days` is authoritative — it is computed server-side so every client agrees
 * on the boundary. We never recompute it from the date string here, because the
 * viewer's timezone would shift the answer by a day either side of midnight.
 */
export function deadlineState(
  deadline: string | null | undefined,
  days: number | null | undefined,
): DeadlineState {
  if (!deadline || days == null) {
    return { tone: 'none', label: 'No deadline', date: null }
  }

  const date = new Date(`${deadline}T00:00:00`).toLocaleDateString(undefined, {
    day: 'numeric', month: 'long', year: 'numeric',
  })

  if (days < 0) {
    const ago = Math.abs(days)
    return {
      tone: 'expired',
      label: ago === 1 ? 'Closed yesterday' : `Closed ${ago} days ago`,
      date,
    }
  }
  if (days === 0) return { tone: 'today', label: 'Closes today', date }
  if (days <= CLOSING_SOON_DAYS) {
    return {
      tone: 'soon',
      label: days === 1 ? 'Closes tomorrow' : `Closes in ${days} days`,
      date,
    }
  }
  return { tone: 'open', label: `Closes ${date}`, date }
}

export const DEADLINE_TONE: Record<DeadlineTone, 'neutral' | 'info' | 'warn' | 'danger'> = {
  expired: 'danger',
  today: 'danger',
  soon: 'warn',
  open: 'neutral',
  none: 'neutral',
}
