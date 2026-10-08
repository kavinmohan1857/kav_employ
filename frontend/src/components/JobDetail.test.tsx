import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import type { Job } from "../types/api";
import { JobDetail } from "./JobDetail";

vi.mock("./ApplicationPanel", () => ({ ApplicationPanel: () => null }));

const neutralJob = {
  id: "example", raw_title: "Engineer", normalized_title: "Engineer",
  raw_company: "Example", raw_location: "Chicago", description: "Build APIs.",
  entry_level_score: 45, entry_level_classification: "uncertain",
  entry_level_reasons: [{ rule: "title.no_senior_keywords", contribution: 0,
    message: "No senior-level keywords were detected in the title" }],
} as Job;

function show(job: Job) {
  render(<JobDetail job={job} onClose={() => {}} onEdit={() => {}}
    onDelete={() => {}} onApplicationChanged={() => {}} />);
}

test("explains the baseline and surfaces missing API analysis", () => {
  show(neutralJob);
  expect(screen.getByText(/No scoring signals were recognized/)).toBeInTheDocument();
  expect(screen.getByText("Personal fit unavailable")).toBeInTheDocument();
});

test("shows evidence and keeps graduation conflicts separate", () => {
  show({ ...neutralJob, personal_fit: {
    version: "personal-fit-v1", score: 10, eligibility: "likely_ineligible",
    findings: [{ category: "graduation", status: "conflicting", contribution: -40,
      evidence: "Must graduate after December 2026.", message: "Graduation falls outside the window" }],
  } });
  expect(screen.getByText("likely ineligible")).toBeInTheDocument();
  expect(screen.getByText("Must graduate after December 2026.")).toBeInTheDocument();
  expect(screen.getByText(/Technical fit remains unverified/)).toBeInTheDocument();
});

test("explains both gaps when no supported requirements were detected", () => {
  show({ ...neutralJob, personal_fit: {
    version: "personal-fit-v1", score: 50, eligibility: "needs_review", findings: [],
  } });
  expect(screen.getByText("needs review")).toBeInTheDocument();
  expect(screen.getByText(/Eligibility remains unverified/)).toBeInTheDocument();
  expect(screen.getByText(/Technical fit remains unverified/)).toBeInTheDocument();
  expect(screen.queryByText("Personal fit unavailable")).not.toBeInTheDocument();
});

test("renders unknown skills with evidence without claiming a mismatch", () => {
  show({ ...neutralJob, personal_fit: {
    version: "personal-fit-v1", score: 50, eligibility: "needs_review",
    findings: [{ category: "skills", status: "unknown", contribution: 0,
      evidence: "AWS required.", message: "AWS experience is unknown" }],
  } });
  expect(screen.getByText("unknown:")).toBeInTheDocument();
  expect(screen.getByText("AWS required.")).toBeInTheDocument();
  expect(screen.getByText(/AWS experience is unknown/)).toBeInTheDocument();
  expect(screen.queryByText(/Technical fit remains unverified/)).not.toBeInTheDocument();
});

test("does not show the neutral-score explanation when scoring signals exist", () => {
  show({ ...neutralJob, entry_level_score: 70, entry_level_classification: "likely",
    entry_level_reasons: [{ rule: "title.level_one", contribution: 25,
      message: "Title identifies a level-one software engineering role" }],
  });
  expect(screen.queryByText(/No scoring signals were recognized/)).not.toBeInTheDocument();
  expect(screen.getByText("+25")).toBeInTheDocument();
});
