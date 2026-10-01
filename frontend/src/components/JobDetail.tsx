import type { Job } from "../types/api";
import { ApplicationPanel } from "./ApplicationPanel";

interface JobDetailProps {
  job: Job;
  onClose: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onApplicationChanged: () => void;
}

function formatSalary(job: Job) {
  if (job.salary_min == null && job.salary_max == null) return null;
  const currency = job.salary_currency ?? "USD";
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  });
  if (job.salary_min != null && job.salary_max != null) {
    return `${formatter.format(job.salary_min)}–${formatter.format(job.salary_max)}`;
  }
  return formatter.format(job.salary_min ?? job.salary_max ?? 0);
}

export function JobDetail({
  job,
  onClose,
  onEdit,
  onDelete,
  onApplicationChanged,
}: JobDetailProps) {
  const salary = formatSalary(job);

  return (
    <article className="detail-panel">
      <div className="detail-header">
        <div>
          <span className="section-kicker">{job.normalized_title}</span>
          <h2>{job.raw_title}</h2>
          <p>{job.raw_company} · {job.raw_location}</p>
        </div>
        <button className="icon-button" type="button" onClick={onClose} aria-label="Close details">×</button>
      </div>

      <div className="detail-actions">
        {job.apply_url && (
          <a className="button button-primary" href={job.apply_url} target="_blank" rel="noreferrer">
            Open application ↗
          </a>
        )}
        <button className="button button-secondary" type="button" onClick={onEdit}>Edit job</button>
        <button className="text-button danger" type="button" onClick={onDelete}>Delete</button>
      </div>

      <section className="score-explanation">
        <div className={`score-ring score-${job.entry_level_classification}`}>
          <strong>{job.entry_level_score}</strong>
          <span>/ 100</span>
        </div>
        <div>
          <span className="section-kicker">Entry-level intelligence</span>
          <h3>{job.entry_level_classification} fit</h3>
          <ul>
            {job.entry_level_reasons.map((reason) => (
              <li key={reason.rule}>
                <span>{reason.contribution > 0 ? "+" : ""}{reason.contribution}</span>
                {reason.message}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="detail-facts">
        <div><span>Workplace</span><strong>{job.workplace_type?.replace("_", " ") ?? "Not specified"}</strong></div>
        <div><span>Employment</span><strong>{job.employment_type?.replace("_", " ") ?? "Not specified"}</strong></div>
        <div><span>Experience</span><strong>{job.minimum_years_experience ?? "?"}–{job.maximum_years_experience ?? "?"} years</strong></div>
        <div><span>Salary</span><strong>{salary ?? "Not listed"}</strong></div>
      </section>

      <section className="description-section">
        <span className="section-kicker">Job description</span>
        <p>{job.description}</p>
      </section>

      <ApplicationPanel jobId={job.id} onChanged={onApplicationChanged} />
    </article>
  );
}
