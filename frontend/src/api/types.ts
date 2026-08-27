export type Role = 'candidate' | 'recruiter'
export type JobType = 'full_time' | 'part_time' | 'contract' | 'internship' | 'remote'
export type JobStatus = 'open' | 'closed'
export type ApplicationStatus =
  | 'applied' | 'reviewed' | 'shortlisted' | 'rejected' | 'hired' | 'withdrawn'

export interface CandidateProfile {
  full_name: string | null
  headline: string | null
  skills: string[]
  resume_url: string | null
}

export interface RecruiterProfile {
  company_name: string | null
  company_website: string | null
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
  required_skills: string[]
  location: string
  job_type: JobType
  salary_min: number | null
  salary_max: number | null
  status: JobStatus
  created_at: string
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
  status: string
  company_name: string | null
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
  skills: string[]
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
  is_mine: boolean
}

export interface Thread {
  application_id: string
  job_title: string
  counterpart_name: string
  messages: ChatMessage[]
}

export interface Suggestion {
  rank: number
  reason: string
  matched_skills: string[]
  overlap: number
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
