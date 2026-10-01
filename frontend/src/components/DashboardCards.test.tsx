import { render, screen } from "@testing-library/react";

import { DashboardCards } from "./DashboardCards";

test("renders dashboard statistics", () => {
  render(
    <DashboardCards
      loading={false}
      summary={{
        total_jobs: 12,
        likely_entry_level_jobs: 7,
        jobs_added_this_week: 4,
        applications_submitted: 3,
      }}
    />,
  );

  expect(screen.getByText("12")).toBeInTheDocument();
  expect(screen.getByText("Likely entry-level")).toBeInTheDocument();
  expect(screen.getByText("3")).toBeInTheDocument();
});
