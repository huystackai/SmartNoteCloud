import { useState } from 'react';

const emptyForm = {
  title: '',
  description: '',
  priority: 'medium',
  deadline: ''
};

export default function TaskForm({ onCreate }) {
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(false);

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    try {
      await onCreate({
        ...form,
        deadline: form.deadline ? new Date(form.deadline).toISOString() : null
      });
      setForm(emptyForm);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="task-form" onSubmit={submit}>
      <div className="task-form-header">
        <span>New task</span>
        <strong>Capture the next deployment step</strong>
      </div>
      <div>
        <label className="form-label">Task title</label>
        <input className="form-control" name="title" value={form.title} onChange={update} required />
      </div>
      <div>
        <label className="form-label">Priority</label>
        <select className="form-select" name="priority" value={form.priority} onChange={update}>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>
      <div>
        <label className="form-label">Deadline</label>
        <input className="form-control" type="datetime-local" name="deadline" value={form.deadline} onChange={update} />
      </div>
      <div className="task-description">
        <label className="form-label">Description</label>
        <textarea className="form-control" name="description" value={form.description} onChange={update} rows="2" />
      </div>
      <button className="btn btn-success task-submit" disabled={loading}>
        {loading ? 'Saving...' : 'Add task'}
      </button>
    </form>
  );
}
