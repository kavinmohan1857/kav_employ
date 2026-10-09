import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import App from "../App";

test("unknown paths show the branded 404 without requesting dashboard data", () => {
  window.history.replaceState({}, "", "/missing-opportunity");
  const fetchSpy = vi.spyOn(window, "fetch");
  try {
    const { unmount } = render(<App />);
    expect(screen.getByRole("heading", { name: "This page didn’t make the shortlist." })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Back to opportunities" })).toHaveAttribute("href", "/#opportunities");
    expect(screen.getByRole("link", { name: "View dashboard" })).toHaveAttribute("href", "/#dashboard");
    expect(document.title).toBe("Page not found | KavEmploy");
    expect(fetchSpy).not.toHaveBeenCalled();
    unmount();
  } finally {
    fetchSpy.mockRestore();
    window.history.replaceState({}, "", "/");
  }
});
