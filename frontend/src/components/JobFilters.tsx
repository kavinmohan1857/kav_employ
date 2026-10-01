import type { FormEvent } from "react";

import type { JobFilters as JobFiltersType } from "../types/api";

interface JobFiltersProps {
  draft: JobFiltersType;
  onChange: (filters: JobFiltersType) => void;
  onApply: () => void;
  onClear: () => void;
}

export function JobFilters({ draft, onChange, onApply, onClear }: JobFiltersProps) {
  function submit(event: FormEvent) {
    event.preventDefault();
    onApply();
  }

  return (
    <form className="filter-panel" onSubmit={submit}>
      <label>
        <span>Role</span>
        <input
          value={draft.title}
          onChange={(event) => onChange({ ...draft, title: event.target.value })}
          placeholder="Software engineer"
        />
      </label>
      <label>
        <span>Company</span>
        <input
          value={draft.company}
          onChange={(event) => onChange({ ...draft, company: event.target.value })}
          placeholder="Company name"
        />
      </label>
      <label>
        <span>Location</span>
        <input
          value={draft.location}
          onChange={(event) => onChange({ ...draft, location: event.target.value })}
          placeholder="Chicago"
        />
      </label>
      <label>
        <span>Suitability</span>
        <select
          value={draft.suitability}
          onChange={(event) =>
            onChange({
              ...draft,
              suitability: event.target.value as JobFiltersType["suitability"],
            })
          }
        >
          <option value="">All scores</option>
          <option value="likely">Likely</option>
          <option value="uncertain">Uncertain</option>
          <option value="unlikely">Unlikely</option>
        </select>
      </label>
      <label>
        <span>Sort</span>
        <select
          value={`${draft.sort_by}:${draft.sort_order}`}
          onChange={(event) => {
            const [sort_by, sort_order] = event.target.value.split(":") as [
              JobFiltersType["sort_by"],
              JobFiltersType["sort_order"],
            ];
            onChange({ ...draft, sort_by, sort_order });
          }}
        >
          <option value="created_at:desc">Newest discovered</option>
          <option value="entry_level_score:desc">Best suitability</option>
          <option value="date_posted:desc">Newest posting</option>
          <option value="created_at:asc">Oldest discovered</option>
        </select>
      </label>
      <div className="filter-actions">
        <button className="button button-secondary" type="button" onClick={onClear}>
          Clear
        </button>
        <button className="button button-primary" type="submit">
          Apply filters
        </button>
      </div>
    </form>
  );
}
