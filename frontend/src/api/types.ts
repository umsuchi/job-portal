export type Role = 'candidate' | 'recruiter'
export type JobType = 'full_time' | 'part_time' | 'contract' | 'internship' | 'temporary'
export type WorkMode = 'onsite' | 'hybrid' | 'remote'
export type ExperienceLevel = 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'principal'
export type JobStatus = 'open' | 'closed'
export type ApplicationStatus =
  | 'applied' | 'reviewed' | 'shortlisted' | 'rejected' | 'hired' | 'withdrawn'

export interface CandidateProfile {
  full_name: string | null
  headline: string | null
  bio: string | null
  avatar_url: string | null
  resume_url: string | null
  location: string | null

  skills: string[]
  years_experience: number | null
  experience_level: ExperienceLevel | null

  preferred_job_types: JobType[]
  preferred_work_modes: WorkMode[]
  preferred_locations: string[]
  desired_salary_min: number | null
  open_to_work: boolean
}

export interface RecruiterProfile {
  company_name: string | null
  company_website: string | null
  avatar_url: string | null
  about: string | null
  industry: string | null
  headquarters: string | null
}

export interface Company {
  name: string | null
  website: string | null
  avatar_url: string | null
  about: string | null
  industry: string | null
  headquarters: string | null
}

export interface User {
  id: string
  email: string
  role: Role
  created_at: string
  candidate_profile: CandidateProfile | null
  recruiter_profile: RecruiterProfile | null
}

export interface Job {
  id: string
  recruiter_id: string

  title: string
  description: string
  responsibilities: string[]
  requirements: string[]
  benefits: string[]

  required_skills: string[]
  nice_to_have_skills: string[]
  experience_level: ExperienceLevel
  min_years_experience: number | null

  location: string
  job_type: JobType
  work_mode: WorkMode
  salary_min: number | null
  salary_max: number | null
  salary_currency: string

  /** Inclusive — applications are accepted all through this day. */
  application_deadline: string | null
  /** Derived server-side, so every client agrees on what expired means. */
  is_expired: boolean
  days_until_deadline: number | null
  accepts_applications: boolean

  status: JobStatus
  created_at: string

  company: Company | null
  company_name: string | null
  application_count: number | null
  has_applied: boolean | null
}

export interface Page<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface JobSummary {
  id: string
  title: string
  location: string
  job_type: string
  work_mode: WorkMode
  experience_level: ExperienceLevel
  application_deadline: string | null
  is_expired: boolean
  status: string
  company_name: string | null
  company_avatar_url: string | null
}

export interface Application {
  id: string
  job_id: string
  candidate_id: string
  cover_note: string | null
  status: ApplicationStatus
  applied_at: string
  job: JobSummary | null
  unread_messages: number
}

export interface CandidateSummary {
  id: string
  email: string
  full_name: string | null
  headline: string | null
  bio: string | null
  avatar_url: string | null
  location: string | null
  skills: string[]
  years_experience: number | null
  experience_level: ExperienceLevel | null
  resume_url: string | null
}

export interface Applicant {
  id: string
  job_id: string
  cover_note: string | null
  status: ApplicationStatus
  applied_at: string
  candidate: CandidateSummary
  unread_messages: number
}

export interface ChatMessage {
  id: string
  application_id: string
  sender_id: string
  receiver_id: string
  body: string
  sent_at: string
  read_at: string | null
  sender_name: string | null
  sender_avatar_url: string | null
  is_mine: boolean
}

export interface Thread {
  application_id: string
  job_title: string
  counterpart_name: string
  counterpart_avatar_url: string | null
  messages: ChatMessage[]
}

export interface Suggestion {
  rank: number
  reason: string
  matched_skills: string[]
  matched_nice_to_have: string[]
  /** Short human-readable reasons this ranked where it did. */
  signals: string[]
  overlap: number
  score: number
  job: Job
}

export interface SuggestionsResponse {
  source: 'ai' | 'fallback'
  generated_at: string
  cached: boolean
  candidate_skills: string[]
  suggestions: Suggestion[]
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}
