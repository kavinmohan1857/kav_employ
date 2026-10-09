import { useCallback, useEffect, useState } from "react";

import { api } from "./api/client";
import { DashboardCards } from "./components/DashboardCards";
import { JobDetail } from "./components/JobDetail";
import { JobFilters } from "./components/JobFilters";
import { JobForm } from "./components/JobForm";
import { JobList } from "./components/JobList";
import { NotFound } from "./components/NotFound";
import type { DashboardSummary, Job, JobFilters as JobFiltersType, JobInput } from "./types/api";

const PAGE_SIZE = 12;
const defaultFilters: JobFiltersType = {
  company: "",
  title: "",
  location: "",
  suitability: "",
  sort_by: "created_at",
  sort_order: "desc",
};

export default function App() {
  return window.location.pathname === "/" ? <Dashboard /> : <NotFound />;
}

function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [filters, setFilters] = useState(defaultFilters);
  const [draftFilters, setDraftFilters] = useState(defaultFilters);
  const [selected, setSelected] = useState<Job | null>(null);
  const [formMode, setFormMode] = useState<"create" | "edit" | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    setSummary(await api.dashboard());
  }, []);

  const loadJobs = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.listJobs(filters, PAGE_SIZE, offset);
      setJobs(result.items);
      setTotal(result.total);
      if (selected) {
        setSelected(result.items.find((job) => job.id === selected.id) ?? selected);
      }
    } finally {
      setLoading(false);
    }
  }, [filters, offset, selected]);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      await Promise.all([loadDashboard(), loadJobs()]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "KavEmploy could not load data");
    }
  }, [loadDashboard, loadJobs]);

  useEffect(() => {
    void refresh();
  }, [filters, offset]); // eslint-disable-line react-hooks/exhaustive-deps

  async function saveJob(input: JobInput) {
    setSaving(true);
    setError(null);
    try {
      const saved = formMode === "edit" && selected
        ? await api.updateJob(selected.id, input)
        : await api.createJob(input);
      setSelected(saved);
      setFormMode(null);
      setOffset(0);
      await Promise.all([loadDashboard(), loadJobs()]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not save this job");
    } finally {
      setSaving(false);
    }
  }

  async function deleteSelected() {
    if (!selected || !window.confirm(`Delete ${selected.raw_title} at ${selected.raw_company}?`)) return;
    try {
      await api.deleteJob(selected.id);
      setSelected(null);
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not delete this job");
    }
  }

  function applyFilters() {
    setOffset(0);
    setFilters(draftFilters);
  }

  function clearFilters() {
    setDraftFilters(defaultFilters);
    setOffset(0);
    setFilters(defaultFilters);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">K</div>
        <div className="brand-copy">
          <strong>KavEmploy</strong>
          <span>Search intelligence</span>
        </div>
        <nav aria-label="Primary navigation">
          <a className="active" href="#opportunities">Opportunities</a>
          <a href="#dashboard">Dashboard</a>
        </nav>
        <div className="sidebar-note">
          <span className="pulse" />
          <p><strong>Local workspace</strong><br />Your data stays in PostgreSQL.</p>
        </div>
      </aside>

      <main>
        <header className="page-header" id="dashboard">
          <div>
            <span className="section-kicker">Class of 2026 · Chicago</span>
            <h1>Your job search, in focus.</h1>
            <p>Capture opportunities. Understand the signals. Move the right roles forward.</p>
          </div>
          <button className="button button-primary add-button" type="button" onClick={() => setFormMode("create")}>
            <span>＋</span> Add opportunity
          </button>
        </header>

        <DashboardCards summary={summary} loading={loading && !summary} />

        <section className="workspace" id="opportunities">
          <div className="section-heading">
            <div>
              <span className="section-kicker">Opportunity pipeline</span>
              <h2>Explore your job library</h2>
            </div>
            <span className="result-count">{total} {total === 1 ? "role" : "roles"}</span>
          </div>

          <JobFilters draft={draftFilters} onChange={setDraftFilters} onApply={applyFilters} onClear={clearFilters} />
          {error && <div className="error-banner"><strong>Something went wrong.</strong> {error}</div>}
          <JobList jobs={jobs} selectedId={selected?.id ?? null} loading={loading} onSelect={setSelected} />

          {total > PAGE_SIZE && (
            <div className="pagination">
              <button className="button button-secondary" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}>Previous</button>
              <span>Page {Math.floor(offset / PAGE_SIZE) + 1} of {Math.ceil(total / PAGE_SIZE)}</span>
              <button className="button button-secondary" disabled={offset + PAGE_SIZE >= total} onClick={() => setOffset(offset + PAGE_SIZE)}>Next</button>
            </div>
          )}
        </section>
      </main>

      {(selected || formMode) && <button className="scrim" aria-label="Close panel" onClick={() => { setSelected(null); setFormMode(null); }} />}
      <aside className={`drawer ${selected || formMode ? "open" : ""}`} aria-live="polite">
        {formMode ? (
          <JobForm job={formMode === "edit" ? selected ?? undefined : undefined} saving={saving} onSubmit={saveJob} onCancel={() => setFormMode(null)} />
        ) : selected ? (
          <JobDetail job={selected} onClose={() => setSelected(null)} onEdit={() => setFormMode("edit")} onDelete={deleteSelected} onApplicationChanged={loadDashboard} />
        ) : null}
      </aside>
    </div>
  );
}
