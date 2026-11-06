import { useEffect, useRef, useState, type DragEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useLoad } from '../../components/useLoad'
import { DashboardShell } from '../../layout/DashboardShell'
import { ALLOWED_EXTENSIONS, MAX_UPLOAD_MB, deleteFile, getCourse, listFiles, uploadFile, type FileStatus } from './api'

interface QueueItem {
  id: number
  name: string
  progress: number
  error?: string
}

const STATUS_LABEL: Record<FileStatus, string> = {
  uploaded: 'Uploaded',
  processing: 'Processing',
  ready: 'Ready',
  failed: 'Failed',
}
const STATUS_CLASS: Record<FileStatus, string> = {
  uploaded: 'pill',
  processing: 'pill pill-warn',
  ready: 'pill pill-ok',
  failed: 'pill pill-err',
}

function validate(file: File): string | null {
  const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
  if (!ALLOWED_EXTENSIONS.includes(ext)) return `Unsupported type. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`
  if (file.size > MAX_UPLOAD_MB * 1024 * 1024) return `Larger than ${MAX_UPLOAD_MB} MB`
  if (file.size === 0) return 'The file is empty'
  return null
}

export default function CourseDetail() {
  const { courseId = '' } = useParams()
  const course = useLoad(() => getCourse(courseId))
  const files = useLoad(() => listFiles(courseId))
  const [queue, setQueue] = useState<QueueItem[]>([])
  const [dragging, setDragging] = useState(false)
  const [deleteError, setDeleteError] = useState('')
  const input = useRef<HTMLInputElement>(null)
  const nextId = useRef(0)

  // While the server is processing files, check back every few seconds.
  const anyProcessing = files.data?.some((f) => f.status === 'processing') ?? false
  const reloadFiles = files.reload
  useEffect(() => {
    if (!anyProcessing) return
    const timer = setInterval(() => void reloadFiles(), 3000)
    return () => clearInterval(timer)
  }, [anyProcessing, reloadFiles])

  const patch = (id: number, change: Partial<QueueItem>) =>
    setQueue((q) => q.map((item) => (item.id === id ? { ...item, ...change } : item)))

  const handleFiles = async (picked: FileList | File[]) => {
    for (const file of Array.from(picked)) {
      const id = nextId.current++
      const problem = validate(file)
      setQueue((q) => [...q, { id, name: file.name, progress: 0, error: problem ?? undefined }])
      if (problem) continue
      try {
        await uploadFile(courseId, file, (progress) => patch(id, { progress }))
        setQueue((q) => q.filter((item) => item.id !== id))
        await Promise.all([files.reload(), course.reload()])
      } catch (err) {
        patch(id, { error: err instanceof Error ? err.message : 'Upload failed' })
      }
    }
  }

  const onDrop = (e: DragEvent) => {
    e.preventDefault()
    setDragging(false)
    void handleFiles(e.dataTransfer.files)
  }

  const remove = async (fileId: string) => {
    setDeleteError('')
    try {
      await deleteFile(courseId, fileId)
      await Promise.all([files.reload(), course.reload()])
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Could not delete the file')
    }
  }

  if (course.error) {
    return (
      <DashboardShell title="Course not found">
        <p className="alert alert-error">{course.error}</p>
        <p><Link to="/teacher/courses">← Back to my courses</Link></p>
      </DashboardShell>
    )
  }

  return (
    <DashboardShell
      title={course.data?.title ?? 'Course'}
      subtitle={course.data ? `${course.data.subject || 'No subject set'} · ${course.data.status}` : undefined}
    >
      <p><Link to="/teacher/courses">← Back to my courses</Link></p>

      <section className="panel">
        <h2>Upload material</h2>
        <div
          className={`dropzone${dragging ? ' dragging' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => input.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && input.current?.click()}
        >
          <strong>Drag files here or click to browse</strong>
          <span>PDF, PowerPoint (.pptx) or Word (.docx) · up to {MAX_UPLOAD_MB} MB each</span>
          <input
            ref={input}
            type="file"
            multiple
            hidden
            accept={ALLOWED_EXTENSIONS.map((e) => `.${e}`).join(',')}
            onChange={(e) => {
              if (e.target.files) void handleFiles(e.target.files)
              e.target.value = ''
            }}
          />
        </div>

        {queue.length > 0 && (
          <ul className="upload-queue">
            {queue.map((item) => (
              <li key={item.id}>
                <div className="upload-row">
                  <span>{item.name}</span>
                  {item.error ? (
                    <button className="link-btn" onClick={() => setQueue((q) => q.filter((i) => i.id !== item.id))}>Dismiss</button>
                  ) : (
                    <span className="muted small">{item.progress}%</span>
                  )}
                </div>
                {item.error ? (
                  <p className="alert alert-error">{item.error}</p>
                ) : (
                  <div className="progress" role="progressbar" aria-valuenow={item.progress} aria-valuemin={0} aria-valuemax={100}>
                    <div style={{ width: `${item.progress}%` }} />
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="panel">
        <h2>Files</h2>
        {files.loading && <p className="muted">Loading…</p>}
        {files.error && <p className="alert alert-error">{files.error}</p>}
        {deleteError && <p className="alert alert-error">{deleteError}</p>}
        {files.data && files.data.length === 0 && <p className="muted">No files uploaded yet.</p>}
        {files.data && files.data.length > 0 && (
          <table className="table">
            <thead><tr><th>Name</th><th>Type</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {files.data.map((f) => (
                <tr key={f.file_id}>
                  <td>{f.file_name}</td>
                  <td>{f.file_type}</td>
                  <td>
                    <span className={STATUS_CLASS[f.status]}>{STATUS_LABEL[f.status]}</span>
                    {f.error_message && <span className="muted small"> {f.error_message}</span>}
                  </td>
                  <td className="actions"><button className="link-btn danger" onClick={() => void remove(f.file_id)}>Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </DashboardShell>
  )
}
