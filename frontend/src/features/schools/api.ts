import { apiFetch } from '../../lib/api'
import type { Role } from '../../lib/api'

export interface School {
  org_id: string
  name: string
  type: 'school' | 'university' | 'company'
  region: 'eu' | 'us'
}

export interface SchoolUser {
  user_id: string
  email: string
  full_name: string
  role: Role
  joined: boolean
}

export const getSchool = () => apiFetch<School>('/api/schools/me')
export const createSchool = (name: string, type: School['type'], region: School['region']) =>
  apiFetch<School>('/api/schools', { method: 'POST', body: JSON.stringify({ name, type, region }) })
export const listSchoolUsers = () => apiFetch<SchoolUser[]>('/api/schools/me/users')
export const inviteUser = (email: string, full_name: string, role: Role) =>
  apiFetch<SchoolUser>('/api/schools/me/users', { method: 'POST', body: JSON.stringify({ email, full_name, role }) })
