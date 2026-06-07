export default function DashboardStats({ stats }) {
  const cards = [
    ['Total', stats.total_tasks, 'All tracked work', 'total'],
    ['Completed', stats.completed_tasks, 'Ready for report', 'completed'],
    ['Pending', stats.pending_tasks, 'Needs attention', 'pending'],
    ['Completion', `${stats.completion_percentage}%`, 'Project progress', 'completion']
  ];

  return (
    <section className="stats-grid">
      {cards.map(([label, value, caption, tone]) => (
        <div className={`stat-card stat-${tone}`} key={label}>
          <span className="stat-label">{label}</span>
          <strong>{value}</strong>
          <small>{caption}</small>
        </div>
      ))}
    </section>
  );
}
