import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from '@/components/Layout'
import { RedirectIfAuthed, RequireAuth } from '@/components/Guards'
import { LoginPage } from '@/pages/Login'
import { RegisterPage } from '@/pages/Register'
import { ProfilePage } from '@/pages/Profile'
import { JobsPage } from '@/pages/Jobs'
import { JobDetailPage } from '@/pages/JobDetail'
import { MyJobsPage } from '@/pages/MyJobs'
import { JobFormPage } from '@/pages/JobForm'
import { ApplicantsPage } from '@/pages/Applicants'
import { MyApplicationsPage } from '@/pages/MyApplications'
import { ThreadPage } from '@/pages/Thread'
import { DashboardPage } from '@/pages/Dashboard'

export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/jobs" replace />} />

        <Route path="/login" element={<RedirectIfAuthed><LoginPage /></RedirectIfAuthed>} />
        <Route path="/register" element={<RedirectIfAuthed><RegisterPage /></RedirectIfAuthed>} />

        <Route path="/jobs" element={<JobsPage />} />
        <Route path="/jobs/:jobId" element={<JobDetailPage />} />

        <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
        <Route
          path="/applications/:applicationId/messages"
          element={<RequireAuth><ThreadPage /></RequireAuth>}
        />

        {/* Candidate */}
        <Route
          path="/dashboard"
          element={<RequireAuth role="candidate"><DashboardPage /></RequireAuth>}
        />
        <Route
          path="/applications"
          element={<RequireAuth role="candidate"><MyApplicationsPage /></RequireAuth>}
        />

        {/* Recruiter */}
        <Route
          path="/my-jobs"
          element={<RequireAuth role="recruiter"><MyJobsPage /></RequireAuth>}
        />
        <Route
          path="/my-jobs/new"
          element={<RequireAuth role="recruiter"><JobFormPage /></RequireAuth>}
        />
        <Route
          path="/my-jobs/:jobId/edit"
          element={<RequireAuth role="recruiter"><JobFormPage /></RequireAuth>}
        />
        <Route
          path="/my-jobs/:jobId/applicants"
          element={<RequireAuth role="recruiter"><ApplicantsPage /></RequireAuth>}
        />

        <Route path="*" element={<Navigate to="/jobs" replace />} />
      </Route>
    </Routes>
  )
}
