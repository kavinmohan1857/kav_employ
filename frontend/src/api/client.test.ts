import { afterEach, describe, expect, test, vi } from "vitest";

import { ApiError, api } from "./client";

afterEach(() => vi.restoreAllMocks());

describe("API client", () => {
  test("builds normalized job filter parameters", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [], total: 0, limit: 20, offset: 0 }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await api.listJobs({
      company: "Acme",
      title: "Software Engineer",
      location: "Chicago",
      suitability: "likely",
      sort_by: "entry_level_score",
      sort_order: "desc",
    });

    const url = String(fetchMock.mock.calls[0][0]);
    expect(url).toContain("company=Acme");
    expect(url).toContain("location=Chicago");
    expect(url).toContain("suitability=likely");
  });

  test("surfaces API validation messages", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: [{ msg: "Title must not be blank" }] }), {
        status: 422,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await expect(api.createJob({
      raw_title: "",
      raw_company: "Acme",
      raw_location: "Chicago",
      description: "Role",
    })).rejects.toEqual(new ApiError("Title must not be blank", 422));
  });
});
