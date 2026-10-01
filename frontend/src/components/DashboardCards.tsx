import type { DashboardSummary } from "../types/api";

interface DashboardCardsProps {
  summary: DashboardSummary | null;
  loading: boolean;
}

const cards: Array<{ key: keyof DashboardSummary; label: string; eyebrow: string }> = [
  { key: "total_jobs", label: "Total opportunities", eyebrow: "Job library" },
  { key: "likely_entry_level_jobs", label: "Likely entry-level", eyebrow: "Strong signals" },
  { key: "jobs_added_this_week", label: "Added this week", eyebrow: "Fresh finds" },
  { key: "applications_submitted", label: "Applications sent", eyebrow: "In motion" },
];

export function DashboardCards({ summary, loading }: DashboardCardsProps) {
  return (
    <section className="metric-grid" aria-label="Job search summary">
      {cards.map((card, index) => (
        <article className={`metric-card metric-card-${index + 1}`} key={card.key}>
          <span className="metric-eyebrow">{card.eyebrow}</span>
          <strong>{loading ? "—" : (summary?.[card.key] ?? 0)}</strong>
          <span>{card.label}</span>
        </article>
      ))}
    </section>
  );
}
