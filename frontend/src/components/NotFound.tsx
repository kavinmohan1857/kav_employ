import { useEffect } from "react";

export function NotFound() {
  useEffect(() => {
    const previousTitle = document.title;
    document.title = "Page not found | KavEmploy";
    return () => { document.title = previousTitle; };
  }, []);

  return (
    <main className="not-found">
      <a className="not-found-brand" href="/" aria-label="KavEmploy home">
        <span className="brand-mark">K</span>
        <strong>KavEmploy</strong>
      </a>
      <section className="not-found-card" aria-labelledby="not-found-title">
        <div className="not-found-art" aria-hidden="true">
          <span className="not-found-number">404</span>
          <span className="not-found-tag">Opportunity not found</span>
        </div>
        <span className="section-kicker">A small detour in your search</span>
        <h1 id="not-found-title">This page didn’t make the shortlist.</h1>
        <p>The link may have moved, or the address might have a typo.
          Your next opportunity is still waiting in your job library.</p>
        <div className="not-found-actions">
          <a className="button button-primary" href="/#opportunities">Back to opportunities</a>
          <a className="button button-secondary" href="/#dashboard">View dashboard</a>
        </div>
        <p className="not-found-footer">Class of 2026. We're gonna make it!!!</p>
      </section>
    </main>
  );
}
