import type { Job } from "../types/api";

interface JobListProps {
  jobs: Job[];
  selectedId: string | null;
  loading: boolean;
  onSelect: (job: Job) => void;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(
    new Date(value),
  );
}

export function JobList({ jobs, selectedId, loading, onSelect }: JobListProps) {
  if (loading) {
    return (
      <div className="job-list" aria-label="Loading jobs">
        {[1, 2, 3].map((item) => (
          <div className="job-card skeleton" key={item} />
        ))}
      </div>
    );
  }

  if (!jobs.length) {
    return (
      <div className="empty-state">
        <span className="empty-mark">⌁</span>
        <h3>No opportunities found</h3>
        <p>Adjust your filters or add a job you want KavEmploy to analyze.</p>
      </div>
    );
  }

  return (
    <div className="job-list">
      {jobs.map((job) => (
        <button
          className={`job-card ${selectedId === job.id ? "selected" : ""}`}
          key={job.id}
          onClick={() => onSelect(job)}
          type="button"
        >
          <div className="job-card-topline">
            <span className={`score-pill score-${job.entry_level_classification}`}>
              {job.entry_level_score}/100 entry-level
            </span>
            <span className="muted">Added {formatDate(job.first_seen_at)}</span>
          </div>
          <h3>{job.raw_title}</h3>
          <p className="company-name">{job.raw_company}</p>
          <div className="job-meta">
            <span>{job.raw_location}</span>
            {job.workplace_type && <span>{job.workplace_type.replace("_", " ")}</span>}
            {job.employment_type && <span>{job.employment_type.replace("_", " ")}</span>}
          </div>
          <p className="job-preview">{job.description}</p>
        </button>
      ))}
    </div>
  );
}
