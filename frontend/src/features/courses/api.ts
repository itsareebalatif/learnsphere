import { API_URL, apiFetch, getAccessToken } from '../../lib/api'

export interface Course {
  course_id: string
  title: string
  subject: string | null
  status: 'draft' | 'published'
  version: number
  file_count: number
  created_at: string
}

export type FileStatus = 'uploaded' | 'processing' | 'ready' | 'failed'

export interface CourseFile {
  file_id: string
  file_name: string
  file_type: string
  status: FileStatus
  error_message: string | null
  uploaded_at: string
}

// Keep in sync with the backend (app/courses/service.py)
export const ALLOWED_EXTENSIONS = ['pdf', 'pptx', 'docx'] // video (mp4, mov, webm) returns with transcription
export const MAX_UPLOAD_MB = 50

export const listCourses = () => apiFetch<Course[]>('/api/courses')
export const getCourse = (id: string) => apiFetch<Course>(`/api/courses/${id}`)
export const createCourse = (title: string, subject: string) =>
  apiFetch<Course>('/api/courses', { method: 'POST', body: JSON.stringify({ title, subject: subject || null }) })
export const listFiles = (id: string) => apiFetch<CourseFile[]>(`/api/courses/${id}/files`)
export const deleteFile = (courseId: string, fileId: string) =>
  apiFetch<void>(`/api/courses/${courseId}/files/${fileId}`, { method: 'DELETE' })

/** Uses XMLHttpRequest because fetch cannot report upload progress. */
export async function uploadFile(courseId: string, file: File, onProgress: (percent: number) => void): Promise<CourseFile> {
  const token = await getAccessToken()
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_URL}/api/courses/${courseId}/files`)
    if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)
    xhr.upload.onprogress = (e) => e.lengthComputable && onProgress(Math.round((e.loaded / e.total) * 100))
    xhr.onload = () => {
      let body: { detail?: unknown } = {}
      try {
        body = JSON.parse(xhr.responseText)
      } catch {
        /* non-JSON response */
      }
      if (xhr.status >= 200 && xhr.status < 300) resolve(body as unknown as CourseFile)
      else reject(new Error(typeof body.detail === 'string' ? body.detail : `Upload failed (${xhr.status})`))
    }
    xhr.onerror = () => reject(new Error('Network error during upload'))
    const form = new FormData()
    form.append('file', file)
    xhr.send(form)
  })
}
