import { useState } from 'react';

export default function AiPanel({ onSuggest }) {
  const [task, setTask] = useState('Lam project Cloud Computing');
  const [mode, setMode] = useState('breakdown');
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await onSuggest(task, mode);
      setSuggestions(result.suggestions || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="ai-panel">
      <div className="section-heading">
        <div>
          <h2>AI Assistant</h2>
          <p>Break work into practical cloud steps.</p>
        </div>
        <span>Mimo API</span>
      </div>
      <form onSubmit={submit}>
        <label className="form-label">Task prompt</label>
        <textarea className="form-control" rows="3" value={task} onChange={(event) => setTask(event.target.value)} />
        <div className="ai-controls">
          <select className="form-select" value={mode} onChange={(event) => setMode(event.target.value)}>
            <option value="breakdown">Breakdown task</option>
            <option value="subtasks">Suggest subtasks</option>
            <option value="summarize">Summarize task</option>
            <option value="productivity">Productivity suggestions</option>
          </select>
          <button className="btn btn-dark" disabled={loading}>{loading ? 'Thinking...' : 'Ask AI'}</button>
        </div>
      </form>
      {error && <div className="alert alert-warning mt-3">{error}</div>}
      {!!suggestions.length && (
        <ol className="suggestions">
          {suggestions.map((item, index) => (
            <li key={`${item}-${index}`}>{item}</li>
          ))}
        </ol>
      )}
    </section>
  );
}
