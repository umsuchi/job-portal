import { api } from './client'
import type {
  Applicant, Application, ApplicationStatus, Job, JobType, Page,
  SuggestionsResponse, Thread, TokenPair, User,
} from './types'

export const auth = {
  register: (body: {
    email: string; password: string; role: 'candidate' | 'recruiter'
    full_name?: string; company_name?: string
  }) => api.post<User>('/auth/register', body).then((r) => r.data),

  login: (body: { email: string; password: string }) =>
    api.post<TokenPair>('/auth/login', body).then((r) => r.data),

  me: () => api.get<User>('/auth/me').then((r) => r.data),

  updateProfile: (body: Partial<{
    full_name: string; headline: string; skills: string[]; resume_url: string
    company_name: string; company_website: string
  }>) => api.put<User>('/auth/me', body).then((r) => r.data),
}

export interface JobFilters {
  q?: string
  skill?: string[]
  location?: string
  job_type?: JobType | ''
  mine?: boolean
  include_closed?: boolean
  limit?: number
  offset?: number
}

export const jobs = {
  list: (filters: JobFilters = {}) =>
    api.get<Page<Job>>('/jobs', {
      params: filters,
      // FastAPI expects repeated `skill=` params, not skill[]=
      paramsSerializer: { indexes: null },
    }).then((r) => r.data),

  get: (id: string) => api.get<Job>(`/jobs/${id}`).then((r) => r.data),

  create: (body: Record<string, unknown>) =>
    api.post<Job>('/jobs', body).then((r) => r.data),

  update: (id: string, body: Record<string, unknown>) =>
    api.put<Job>(`/jobs/${id}`, body).then((r) => r.data),

  close: (id: string) => api.delete<Job>(`/jobs/${id}`).then((r) => r.data),

  applicants: (id: string) =>
    api.get<Applicant[]>(`/jobs/${id}/applications`).then((r) => r.data),
}

export const applications = {
  apply: (body: { job_id: string; cover_note?: string }) =>
    api.post<Application>('/applications', body).then((r) => r.data),

  mine: () => api.get<Application[]>('/applications/me').then((r) => r.data),

  get: (id: string) => api.get<Application>(`/applications/${id}`).then((r) => r.data),

  setStatus: (id: string, status: Exclude<ApplicationStatus, 'applied' | 'withdrawn'>) =>
    api.patch<Application>(`/applications/${id}/status`, { status }).then((r) => r.data),

  withdraw: (id: string) =>
    api.delete<Application>(`/applications/${id}`).then((r) => r.data),
}

export const messages = {
  thread: (applicationId: string) =>
    api.get<Thread>(`/applications/${applicationId}/messages`).then((r) => r.data),

  send: (applicationId: string, body: string) =>
    api.post(`/applications/${applicationId}/messages`, { body }).then((r) => r.data),

  unreadCount: () =>
    api.get<{ unread: number }>('/messages/unread-count').then((r) => r.data),
}

export const suggestions = {
  list: (refresh = false) =>
    api.get<SuggestionsResponse>('/suggestions', { params: { refresh } }).then((r) => r.data),
}
