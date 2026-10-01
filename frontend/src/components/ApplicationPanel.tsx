import { useEffect, useState, type FormEvent } from "react";

import { ApiError, api } from "../api/client";
import type { ApplicationStatus, ApplicationTracking } from "../types/api";

interface ApplicationPanelProps {
  jobId: string;
  onChanged: () => void;
}

const statuses: ApplicationStatus[] = [
  "saved",
  "applied",
  "interview",
  "rejected",
  "offer",
  "withdrawn",
];

export function ApplicationPanel({ jobId, onChanged }: ApplicationPanelProps) {
  const [tracking, setTracking] = useState<ApplicationTracking | null>(null);
  const [status, setStatus] = useState<ApplicationStatus>("saved");
  const [notes, setNotes] = useState("");
  const [referral, setReferral] = useState(false);
  const [interviewStage, setInterviewStage] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setError(null);
    api
      .getApplication(jobId)
      .then((result) => {
        if (!active) return;
        setTracking(result);
        setStatus(result.status);
        setNotes(result.notes ?? "");
        setReferral(result.referral);
        setInterviewStage(result.interview_stage ?? "");
      })
      .catch((caught: unknown) => {
        if (!active) return;
        if (caught instanceof ApiError && caught.status === 404) {
          setTracking(null);
          setStatus("saved");
          setNotes("");
          setReferral(false);
          setInterviewStage("");
        } else {
          setError(caught instanceof Error ? caught.message : "Could not load application status");
        }
      });
    return () => {
      active = false;
    };
  }, [jobId]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const result = await api.saveApplication(jobId, {
        status,
        notes: notes || null,
        referral,
        interview_stage: status === "interview" ? interviewStage || null : null,
      });
      setTracking(result);
      onChanged();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not save application status");
    } finally {
      setSaving(false);
    }
  }

  async function remove() {
    setSaving(true);
    setError(null);
    try {
      await api.deleteApplication(jobId);
      setTracking(null);
      setStatus("saved");
      setNotes("");
      setReferral(false);
      setInterviewStage("");
      onChanged();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not remove tracking");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="application-panel" onSubmit={submit}>
      <div className="section-heading compact">
        <div>
          <span className="section-kicker">Your progress</span>
          <h3>Application tracker</h3>
        </div>
        {tracking?.date_applied && (
          <span className="applied-date">
            Applied {new Date(tracking.date_applied).toLocaleDateString()}
          </span>
        )}
      </div>

      <div className="status-row" aria-label="Application status">
        {statuses.map((option) => (
          <button
            type="button"
            className={status === option ? "status-option active" : "status-option"}
            onClick={() => setStatus(option)}
            key={option}
          >
            {option}
          </button>
        ))}
      </div>

      {status === "interview" && (
        <label>
          <span>Interview stage</span>
          <input
            value={interviewStage}
            onChange={(event) => setInterviewStage(event.target.value)}
            placeholder="Recruiter screen, technical…"
          />
        </label>
      )}

      <label>
        <span>Notes</span>
        <textarea
          rows={3}
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          placeholder="Contacts, next steps, preparation notes…"
        />
      </label>

      <label className="checkbox-label">
        <input type="checkbox" checked={referral} onChange={(event) => setReferral(event.target.checked)} />
        <span>I have a referral for this role</span>
      </label>

      {error && <p className="inline-error">{error}</p>}
      <div className="tracker-actions">
        {tracking && (
          <button className="text-button danger" type="button" onClick={remove} disabled={saving}>
            Remove tracking
          </button>
        )}
        <button className="button button-primary" type="submit" disabled={saving}>
          {saving ? "Saving…" : tracking ? "Update status" : "Start tracking"}
        </button>
      </div>
    </form>
  );
}
