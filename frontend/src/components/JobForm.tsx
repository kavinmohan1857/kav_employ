import { useState, type FormEvent } from "react";

import type { Job, JobInput } from "../types/api";

interface JobFormProps {
  job?: Job;
  saving: boolean;
  onSubmit: (input: JobInput) => Promise<void>;
  onCancel: () => void;
}

function initialValues(job?: Job): Record<string, string> {
  return {
    raw_title: job?.raw_title ?? "",
    raw_company: job?.raw_company ?? "",
    raw_location: job?.raw_location ?? "Chicago, IL",
    description: job?.description ?? "",
    workplace_type: job?.workplace_type ?? "",
    employment_type: job?.employment_type ?? "full_time",
    source: job?.source ?? "manual",
    apply_url: job?.apply_url ?? "",
    date_posted: job?.date_posted?.slice(0, 10) ?? "",
    minimum_years_experience: job?.minimum_years_experience?.toString() ?? "",
    maximum_years_experience: job?.maximum_years_experience?.toString() ?? "",
    salary_min: job?.salary_min?.toString() ?? "",
    salary_max: job?.salary_max?.toString() ?? "",
    salary_currency: job?.salary_currency ?? "USD",
  };
}

function optionalNumber(value: string): number | null {
  return value === "" ? null : Number(value);
}

export function JobForm({ job, saving, onSubmit, onCancel }: JobFormProps) {
  const [values, setValues] = useState(() => initialValues(job));

  function update(field: string, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    await onSubmit({
      raw_title: values.raw_title,
      raw_company: values.raw_company,
      raw_location: values.raw_location,
      description: values.description,
      workplace_type: (values.workplace_type || null) as JobInput["workplace_type"],
      employment_type: (values.employment_type || null) as JobInput["employment_type"],
      source: values.source,
      apply_url: values.apply_url || null,
      date_posted: values.date_posted ? `${values.date_posted}T00:00:00Z` : null,
      minimum_years_experience: optionalNumber(values.minimum_years_experience),
      maximum_years_experience: optionalNumber(values.maximum_years_experience),
      salary_min: optionalNumber(values.salary_min),
      salary_max: optionalNumber(values.salary_max),
      salary_currency: values.salary_currency || null,
    });
  }

  return (
    <form className="job-form" onSubmit={submit}>
      <div className="form-heading">
        <div>
          <span className="section-kicker">{job ? "Update record" : "New opportunity"}</span>
          <h2>{job ? "Edit job" : "Add a job"}</h2>
        </div>
        <button className="icon-button" type="button" onClick={onCancel} aria-label="Close form">
          ×
        </button>
      </div>

      <div className="form-grid">
        <label className="span-2">
          <span>Job title *</span>
          <input required maxLength={300} value={values.raw_title} onChange={(e) => update("raw_title", e.target.value)} />
        </label>
        <label>
          <span>Company *</span>
          <input required maxLength={300} value={values.raw_company} onChange={(e) => update("raw_company", e.target.value)} />
        </label>
        <label>
          <span>Location *</span>
          <input required maxLength={300} value={values.raw_location} onChange={(e) => update("raw_location", e.target.value)} />
        </label>
        <label>
          <span>Workplace</span>
          <select value={values.workplace_type} onChange={(e) => update("workplace_type", e.target.value)}>
            <option value="">Not specified</option>
            <option value="on_site">On-site</option>
            <option value="hybrid">Hybrid</option>
            <option value="remote">Remote</option>
            <option value="unknown">Unknown</option>
          </select>
        </label>
        <label>
          <span>Employment</span>
          <select value={values.employment_type} onChange={(e) => update("employment_type", e.target.value)}>
            <option value="">Not specified</option>
            <option value="full_time">Full-time</option>
            <option value="part_time">Part-time</option>
            <option value="contract">Contract</option>
            <option value="internship">Internship</option>
            <option value="unknown">Unknown</option>
          </select>
        </label>
        <label>
          <span>Minimum experience</span>
          <input type="number" min="0" max="99" step="0.5" value={values.minimum_years_experience} onChange={(e) => update("minimum_years_experience", e.target.value)} />
        </label>
        <label>
          <span>Maximum experience</span>
          <input type="number" min="0" max="99" step="0.5" value={values.maximum_years_experience} onChange={(e) => update("maximum_years_experience", e.target.value)} />
        </label>
        <label>
          <span>Salary minimum</span>
          <input type="number" min="0" step="1000" value={values.salary_min} onChange={(e) => update("salary_min", e.target.value)} />
        </label>
        <label>
          <span>Salary maximum</span>
          <input type="number" min="0" step="1000" value={values.salary_max} onChange={(e) => update("salary_max", e.target.value)} />
        </label>
        <label>
          <span>Currency</span>
          <input maxLength={3} value={values.salary_currency} onChange={(e) => update("salary_currency", e.target.value.toUpperCase())} />
        </label>
        <label>
          <span>Date posted</span>
          <input type="date" value={values.date_posted} onChange={(e) => update("date_posted", e.target.value)} />
        </label>
        <label className="span-2">
          <span>Application URL</span>
          <input type="url" value={values.apply_url} onChange={(e) => update("apply_url", e.target.value)} placeholder="https://" />
        </label>
        <label className="span-2">
          <span>Description *</span>
          <textarea required rows={8} value={values.description} onChange={(e) => update("description", e.target.value)} />
        </label>
      </div>

      <div className="form-actions">
        <button className="button button-secondary" type="button" onClick={onCancel}>Cancel</button>
        <button className="button button-primary" type="submit" disabled={saving}>
          {saving ? "Saving…" : job ? "Save changes" : "Analyze & save"}
        </button>
      </div>
    </form>
  );
}
