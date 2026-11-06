import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth/AuthProvider'
import { useAuth } from './auth/context'
import { ProtectedRoute, PublicOnlyRoute } from './auth/ProtectedRoute'
import CourseDetail from './features/courses/CourseDetail'
import CoursesPage from './features/courses/CoursesPage'
import ClassDetail from './features/classes/ClassDetail'
import StudentDashboard from './features/classes/StudentDashboard'
import TeacherDashboard from './features/classes/TeacherDashboard'
import AdminDashboard from './features/schools/AdminDashboard'
import Dashboard from './pages/Dashboard'
import ForgotPassword from './pages/ForgotPassword'
import Login from './pages/Login'
import ResetPassword from './pages/ResetPassword'
import Signup from './pages/Signup'
import './App.css'

function Home() {
  const { profile, loading } = useAuth()
  if (loading) return <p className="center-msg">Loading…</p>
  return <Navigate to={profile ? `/${profile.role}` : '/login'} replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route element={<PublicOnlyRoute />}>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
          </Route>
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route element={<ProtectedRoute roles={['admin']} />}>
            <Route path="/admin" element={<AdminDashboard />} />
          </Route>
          <Route element={<ProtectedRoute roles={['teacher']} />}>
            <Route path="/teacher" element={<TeacherDashboard />} />
            <Route path="/teacher/classes/:classId" element={<ClassDetail />} />
            <Route path="/teacher/courses" element={<CoursesPage />} />
            <Route path="/teacher/courses/:courseId" element={<CourseDetail />} />
          </Route>
          <Route element={<ProtectedRoute roles={['student']} />}>
            <Route path="/student" element={<StudentDashboard />} />
          </Route>
          <Route element={<ProtectedRoute roles={['parent']} />}>
            <Route path="/parent" element={<Dashboard />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
