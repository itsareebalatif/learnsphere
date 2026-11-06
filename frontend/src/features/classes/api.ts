import { apiFetch } from '../../lib/api'

export interface SchoolClass {
  class_id: string
  name: string
  term: string | null
  teacher_name: string
  student_count: number
  created_at: string
}

export interface Student {
  user_id: string
  email: string
  full_name: string
  joined: boolean
}

export const listClasses = () => apiFetch<SchoolClass[]>('/api/classes')
export const getClass = (id: string) => apiFetch<SchoolClass>(`/api/classes/${id}`)
export const createClass = (name: string, term: string) =>
  apiFetch<SchoolClass>('/api/classes', { method: 'POST', body: JSON.stringify({ name, term: term || null }) })
export const listStudents = (id: string) => apiFetch<Student[]>(`/api/classes/${id}/students`)
export const addStudent = (id: string, email: string, full_name: string) =>
  apiFetch<Student>(`/api/classes/${id}/students`, {
    method: 'POST',
    body: JSON.stringify({ email, full_name: full_name || null }),
  })
