export type Suitability = "likely" | "uncertain" | "unlikely";
export type ApplicationStatus =
  | "saved"
  | "applied"
  | "interview"
  | "rejected"
  | "offer"
  | "withdrawn";

export interface ClassificationReason {
  rule: string;
  contribution: number;
  message: string;
}

export interface Job {
  id: string;
  raw_title: string;
  normalized_title: string;
  raw_company: string;
  normalized_company: string;
  raw_location: string;
  normalized_location: string;
  workplace_type: "on_site" | "hybrid" | "remote" | "unknown" | null;
  description: string;
  source: string;
  source_external_id: string | null;
  source_url: string | null;
  apply_url: string | null;
  date_posted: string | null;
  first_seen_at: string;
  last_seen_at: string;
  employment_type: "full_time" | "part_time" | "contract" | "internship" | "unknown" | null;
  minimum_years_experience: number | null;
  maximum_years_experience: number | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  entry_level_score: number;
  personal_fit?: {
    version: string;
    eligibility: "likely_eligible" | "likely_ineligible" | "needs_review";
    score: number;
    findings: Array<{
      category: "graduation" | "skills";
      status: "satisfied" | "conflicting" | "unknown";
      contribution: number;
      evidence: string;
      message: string;
    }>;
  };
  entry_level_reasons: ClassificationReason[];
  entry_level_classification: Suitability;
  classifier_version: string;
  duplicate_fingerprint: string;
  created_at: string;
  updated_at: string;
}

export interface JobInput {
  raw_title: string;
  raw_company: string;
  raw_location: string;
  description: string;
  workplace_type?: Job["workplace_type"];
  employment_type?: Job["employment_type"];
  source?: string;
  source_url?: string | null;
  apply_url?: string | null;
  date_posted?: string | null;
  minimum_years_experience?: number | null;
  maximum_years_experience?: number | null;
  salary_min?: number | null;
  salary_max?: number | null;
  salary_currency?: string | null;
}

export interface JobListResponse {
  items: Job[];
  total: number;
  limit: number;
  offset: number;
}

export interface DashboardSummary {
  total_jobs: number;
  likely_entry_level_jobs: number;
  jobs_added_this_week: number;
  applications_submitted: number;
}

export interface ApplicationTracking {
  id: string;
  job_id: string;
  status: ApplicationStatus;
  date_applied: string | null;
  notes: string | null;
  referral: boolean;
  interview_stage: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationInput {
  status: ApplicationStatus;
  date_applied?: string | null;
  notes?: string | null;
  referral?: boolean;
  interview_stage?: string | null;
}

export interface JobFilters {
  company: string;
  title: string;
  location: string;
  suitability: "" | Suitability;
  sort_by: "created_at" | "date_posted" | "entry_level_score";
  sort_order: "asc" | "desc";
}
