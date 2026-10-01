import type {
  ApplicationInput,
  ApplicationTracking,
  DashboardSummary,
  Job,
  JobFilters,
  JobInput,
  JobListResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string | Array<{ msg?: string }> };
      if (typeof body.detail === "string") message = body.detail;
      else if (Array.isArray(body.detail)) {
        message = body.detail.map((issue) => issue.msg ?? "Invalid value").join("; ");
      }
    } catch {
      // Preserve the status-based fallback for non-JSON errors.
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<DashboardSummary>("/api/v1/dashboard/summary"),
  listJobs: (filters: JobFilters, limit = 20, offset = 0) => {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
    });
    if (filters.company) params.set("company", filters.company);
    if (filters.title) params.set("title", filters.title);
    if (filters.location) params.set("location", filters.location);
    if (filters.suitability) params.set("suitability", filters.suitability);
    return request<JobListResponse>(`/api/v1/jobs?${params}`);
  },
  getJob: (id: string) => request<Job>(`/api/v1/jobs/${id}`),
  createJob: (input: JobInput) =>
    request<Job>("/api/v1/jobs", { method: "POST", body: JSON.stringify(input) }),
  updateJob: (id: string, input: Partial<JobInput>) =>
    request<Job>(`/api/v1/jobs/${id}`, { method: "PATCH", body: JSON.stringify(input) }),
  deleteJob: (id: string) => request<void>(`/api/v1/jobs/${id}`, { method: "DELETE" }),
  getApplication: (jobId: string) =>
    request<ApplicationTracking>(`/api/v1/jobs/${jobId}/application`),
  saveApplication: (jobId: string, input: ApplicationInput) =>
    request<ApplicationTracking>(`/api/v1/jobs/${jobId}/application`, {
      method: "PUT",
      body: JSON.stringify(input),
    }),
  deleteApplication: (jobId: string) =>
    request<void>(`/api/v1/jobs/${jobId}/application`, { method: "DELETE" }),
};
