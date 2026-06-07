import { useState } from 'react';

export default function TaskList({ tasks, onUpdate, onComplete, onDelete }) {
  const [editingId, setEditingId] = useState(null);
  const [draft, setDraft] = useState({});

  function startEdit(task) {
    setEditingId(task.id);
    setDraft({
      title: task.title,
      description: task.description || '',
      priority: task.priority,
      status: task.status,
      deadline: task.deadline ? task.deadline.slice(0, 16) : ''
    });
  }

  async function save(taskId) {
    await onUpdate(taskId, {
      ...draft,
      deadline: draft.deadline ? new Date(draft.deadline).toISOString() : null
    });
    setEditingId(null);
  }

  if (!tasks.length) {
    return (
      <div className="empty-state">
        <strong>No tasks yet</strong>
        <span>Create the first deployment step to start the dashboard.</span>
      </div>
    );
  }

  return (
    <div className="task-list">
      {tasks.map((task) => {
        const editing = editingId === task.id;
        return (
          <article className={`task-item ${task.status === 'completed' ? 'is-completed' : ''}`} key={task.id}>
            {editing ? (
              <div className="edit-grid">
                <input
                  className="form-control"
                  value={draft.title}
                  onChange={(event) => setDraft({ ...draft, title: event.target.value })}
                />
                <select
                  className="form-select"
                  value={draft.priority}
                  onChange={(event) => setDraft({ ...draft, priority: event.target.value })}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
                <input
                  className="form-control"
                  type="datetime-local"
                  value={draft.deadline}
                  onChange={(event) => setDraft({ ...draft, deadline: event.target.value })}
                />
                <textarea
                  className="form-control"
                  rows="2"
                  value={draft.description}
                  onChange={(event) => setDraft({ ...draft, description: event.target.value })}
                />
                <div className="actions">
                  <button className="btn btn-primary btn-sm" onClick={() => save(task.id)}>Save</button>
                  <button className="btn btn-outline-secondary btn-sm" onClick={() => setEditingId(null)}>Cancel</button>
                </div>
              </div>
            ) : (
              <>
                <div className="task-main">
                  <div>
                    <h3>{task.title}</h3>
                    {task.description && <p>{task.description}</p>}
                    {task.ai_summary && <p className="ai-summary">{task.ai_summary}</p>}
                  </div>
                  <div className="task-meta">
                    <span className={`priority priority-${task.priority}`}>{task.priority}</span>
                    <span className={`status status-${task.status}`}>{task.status}</span>
                    {task.deadline && <span>{new Date(task.deadline).toLocaleString()}</span>}
                  </div>
                </div>
                <div className="actions">
                  {task.status !== 'completed' && (
                    <button className="btn btn-outline-success btn-sm" onClick={() => onComplete(task.id)}>Done</button>
                  )}
                  <button className="btn btn-outline-primary btn-sm" onClick={() => startEdit(task)}>Edit</button>
                  <button className="btn btn-outline-danger btn-sm" onClick={() => onDelete(task.id)}>Delete</button>
                </div>
              </>
            )}
          </article>
        );
      })}
    </div>
  );
}
