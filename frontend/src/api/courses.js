import http from './http'

// ── 课程 ──────────────────────────────────────────────────────────────────────
export const getCourses     = (teacher_id)        => http.get('/api/courses', { params: { teacher_id } }).then(r => r.data)
export const createCourse   = (data)              => http.post('/api/courses', data).then(r => r.data)
export const deleteCourse   = (id)                => http.delete(`/api/courses/${id}`).then(r => r.data)

// ── 班级 ──────────────────────────────────────────────────────────────────────
export const getClasses     = (course_id)         => http.get(`/api/courses/${course_id}/classes`).then(r => r.data)
export const createClass    = (course_id, data)   => http.post(`/api/courses/${course_id}/classes`, data).then(r => r.data)
export const getClass       = (class_id)          => http.get(`/api/classes/${class_id}`).then(r => r.data)
export const updateClass    = (class_id, data)    => http.patch(`/api/classes/${class_id}`, data).then(r => r.data)
export const deleteClass    = (class_id)          => http.delete(`/api/classes/${class_id}`).then(r => r.data)
export const getMyClasses   = (student_id)        => http.get('/api/my/classes', { params: { student_id } }).then(r => r.data)

// ── 成员 ──────────────────────────────────────────────────────────────────────
export const getMembers     = (class_id)          => http.get(`/api/classes/${class_id}/members`).then(r => r.data)
export const addMember      = (class_id, data)    => http.post(`/api/classes/${class_id}/members`, data).then(r => r.data)
export const removeMember   = (class_id, sid)     => http.delete(`/api/classes/${class_id}/members/${sid}`).then(r => r.data)

// ── 作业 ──────────────────────────────────────────────────────────────────────
export const getAssignments     = (class_id)           => http.get(`/api/classes/${class_id}/assignments`).then(r => r.data)
export const createAssignment   = (class_id, data)     => http.post(`/api/classes/${class_id}/assignments`, data).then(r => r.data)
export const getAssignment      = (id)                 => http.get(`/api/assignments/${id}`).then(r => r.data)
export const updateAssignment   = (id, data)           => http.patch(`/api/assignments/${id}`, data).then(r => r.data)
export const deleteAssignment   = (id)                 => http.delete(`/api/assignments/${id}`).then(r => r.data)

// ── 提交 ──────────────────────────────────────────────────────────────────────
export const getSubmissions     = (assignment_id)                 => http.get(`/api/assignments/${assignment_id}/submissions`).then(r => r.data)
export const getMySubmission    = (assignment_id, student_id)     => http.get(`/api/assignments/${assignment_id}/my-submission`, { params: { student_id } }).then(r => r.data)
export const submitAssignment   = (assignment_id, data)           => http.post(`/api/assignments/${assignment_id}/submit`, data).then(r => r.data)
export const submitFile         = (assignment_id, formData)       => http.post(`/api/assignments/${assignment_id}/submit-file`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
export const gradeSubmission    = (submission_id, data)           => http.patch(`/api/submissions/${submission_id}`, data).then(r => r.data)

// ── 情绪打卡 ──────────────────────────────────────────────────────────────────
export const getCheckinProgress = (assignment_id, student_id)     => http.get(`/api/assignments/${assignment_id}/checkin-progress`, { params: { student_id } }).then(r => r.data)
export const getCheckinStats    = (assignment_id)                  => http.get(`/api/assignments/${assignment_id}/checkin-stats`).then(r => r.data)

// ── 全班讨论 ──────────────────────────────────────────────────────────────────
export const getThreads     = (class_id)          => http.get(`/api/classes/${class_id}/threads`).then(r => r.data)
export const createThread   = (class_id, data)    => http.post(`/api/classes/${class_id}/threads`, data).then(r => r.data)
export const getThread      = (thread_id)         => http.get(`/api/threads/${thread_id}`).then(r => r.data)
export const addReply       = (thread_id, data)   => http.post(`/api/threads/${thread_id}/replies`, data).then(r => r.data)
export const deleteThread   = (thread_id)         => http.delete(`/api/threads/${thread_id}`).then(r => r.data)
export const deleteReply    = (reply_id)          => http.delete(`/api/replies/${reply_id}`).then(r => r.data)
export const pinThread      = (thread_id)         => http.patch(`/api/threads/${thread_id}/pin`).then(r => r.data)

// ── 小组讨论 ──────────────────────────────────────────────────────────────────
export const getGroups      = (class_id)          => http.get(`/api/classes/${class_id}/groups`).then(r => r.data)
export const createGroup    = (class_id, data)    => http.post(`/api/classes/${class_id}/groups`, data).then(r => r.data)
export const updateGroup    = (group_id, data)    => http.patch(`/api/groups/${group_id}`, data).then(r => r.data)
export const deleteGroup    = (group_id)          => http.delete(`/api/groups/${group_id}`).then(r => r.data)
export const getMyGroup     = (class_id, student_id) => http.get('/api/my-group', { params: { class_id, student_id } }).then(r => r.data)
export const getMessages    = (group_id)          => http.get(`/api/groups/${group_id}/messages`).then(r => r.data)
export const sendMessage    = (group_id, data)    => http.post(`/api/groups/${group_id}/messages`, data).then(r => r.data)
