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
          <p>This score estimates whether the role is entry-level. It starts at 45;
            recognized title, experience, and education signals adjust it. It is not a percentage match to your resume.</p>
          {job.entry_level_reasons.every((reason) => reason.contribution === 0) && (
            <p>No scoring signals were recognized, so the score stays at 45.
              A title without senior keywords alone does not establish an entry-level role.
              Review the description and the personal requirements below.</p>
          )}
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

      {job.personal_fit ? (
        <section className="description-section">
          <span className="section-kicker">Personal fit</span>
          <h3>{job.personal_fit.eligibility.replaceAll("_", " ")}</h3>
          <p>Rule score: {job.personal_fit.score}/100. Unrecorded skills need review.</p>
          <p>Graduation eligibility and technical requirements are evaluated separately from the entry-level score.
            A graduation conflict requires attention even when skills match.</p>
          {!job.personal_fit.findings.some((finding) => finding.category === "graduation") && (
            <p>Graduation: no supported date requirement was detected. Eligibility remains unverified.</p>
          )}
          {!job.personal_fit.findings.some((finding) => finding.category === "skills") && (
            <p>Skills: no technologies from the supported vocabulary were detected. Technical fit remains unverified.</p>
          )}
          <ul>
            {job.personal_fit.findings.map((finding, index) => (
              <li key={index}>
                <strong>{finding.status}: </strong>{finding.message}
                <span> ({finding.contribution > 0 ? "+" : ""}{finding.contribution} points)</span>
                <blockquote>{finding.evidence}</blockquote>
              </li>
            ))}
          </ul>
        </section>
      ) : (
        <section className="description-section" role="status">
          <span className="section-kicker">Personal fit unavailable</span>
          <p>The API did not return graduation or skill analysis. Restart the backend with the latest code,
            then refresh this page.</p>
        </section>
      )}

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
