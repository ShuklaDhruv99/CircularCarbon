import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getHealth } from "../services/api";
import { getActiveFactoryId, isLoggedIn } from "../services/persistence";
import type { HealthStatus } from "../types";

function HomePage() {
  const [shouldRedirect, setShouldRedirect] = useState(false);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isLoggedIn() && getActiveFactoryId()) setShouldRedirect(true);
    getHealth()
      .then((result) => setHealth(result))
      .catch(() => setError("Unable to reach backend API."));
  }, []);

  if (shouldRedirect) {
    const factoryId = getActiveFactoryId();
    if (factoryId) window.location.replace(`/factories/${factoryId}/emissions`);
  }

  return (
    <div className="app-shell">
      <div className="page-frame">
        <nav className="marketing-nav">
          <Link to="/" className="brand"><span className="brand-mark" />CircularCarbon</Link>
          <div className="nav-links">
            <a href="#method">How it works</a>
              <a href="#signals">Signals</a>
              <a href="#product">Product</a>
            <span className="nav-status"><span className="status-dot" />{error ? "API offline" : health?.status === "ok" ? "Systems online" : "Connecting"}</span>
          </div>
        </nav>

        <main>
          <section className="hero">
            <div className="hero-copy">
              <span className="eyebrow">Industrial intelligence / 01</span>
              <h1 className="display">Find where your factory is <em>losing carbon efficiency.</em></h1>
              <p>CircularCarbon AI maps energy, materials and waste into a clear path from emission hotspots to decisions worth making.</p>
              <div className="hero-actions">
                <Link to="/onboarding" className="primary-btn">Start free assessment <span>↗</span></Link>
                <a href="#method" className="secondary-btn">See how it works</a>
              </div>
              <p className="hero-note">No sensors required for the initial assessment.</p>
              <div className="hero-stats">
                <div className="hero-stat"><strong>4 steps</strong><span>from data to action</span></div>
                <div className="hero-stat"><strong>80%</strong><span>hotspot prioritisation</span></div>
                <div className="hero-stat"><strong>AI-led</strong><span>recommendations</span></div>
              </div>
            </div>
            <div className="hero-visual">
              <div className="process-card">
                <div className="process-head"><span className="process-label">Assessment map</span><span className="process-total mono">LIVE MODEL</span></div>
                <div className="flow">
                  <div className="flow-node"><span className="flow-index">01</span><span><span className="flow-name">Raw material</span><br /><span className="flow-meta">inputs & sourcing</span></span><span className="flow-value mono">→ 14.2</span></div>
                  <div className="flow-node"><span className="flow-index">02</span><span><span className="flow-name">Processing</span><br /><span className="flow-meta">energy & production</span></span><span className="flow-value mono">→ 62.8</span></div>
                  <div className="flow-node"><span className="flow-index">03</span><span><span className="flow-name">Waste stream</span><br /><span className="flow-meta">reuse & recovery</span></span><span className="flow-value mono">→ 08.6</span></div>
                  <div className="flow-node"><span className="flow-index">04</span><span><span className="flow-name">Action plan</span><br /><span className="flow-meta">ranked by impact</span></span><span className="flow-value mono">→ 03.1</span></div>
                </div>
              </div>
            </div>
          </section>

          <section className="feature-strip" id="method">
            <div className="feature"><span className="feature-number mono">01 / ASSESS</span><h3>Turn operating data into signal</h3><p>Capture the minimum viable picture of your facility without waiting for a perfect data set.</p></div>
            <div className="feature"><span className="feature-number mono">02 / DISCOVER</span><h3>See the hotspots that matter</h3><p>Surface the processes and activities with the highest contribution to your footprint.</p></div>
            <div className="feature"><span className="feature-number mono">03 / ACT</span><h3>Choose moves with a return</h3><p>Compare circular alternatives by reduction, cost and payback — then make the next move.</p></div>
          </section>
          <section className="landing-section signal-section" id="signals">
            <div><span className="eyebrow">The operating picture / 02</span><h2>One view of the decisions hiding inside your data.</h2><p>Stop managing carbon in disconnected spreadsheets. See what is driving your footprint, what it costs, and where action pays back.</p></div>
            <div className="signal-board"><div className="signal-board-top"><span className="mono">FACILITY SIGNALS</span><span className="signal-live">● LIVE</span></div><div className="signal-row"><span>Energy intensity</span><strong>62.8 <small>kg CO₂e</small></strong><i className="signal-bar high" /></div><div className="signal-row"><span>Material inputs</span><strong>14.2 <small>kg CO₂e</small></strong><i className="signal-bar mid" /></div><div className="signal-row"><span>Waste recovery gap</span><strong>08.6 <small>kg CO₂e</small></strong><i className="signal-bar low" /></div><div className="signal-foot"><span>Top hotspot</span><strong>Electricity / Processing</strong></div></div>
          </section>
          <section className="landing-section workflow-section" id="product">
            <div className="section-heading"><span className="eyebrow">Built for the whole loop / 03</span><h2>From first assessment to next best action.</h2></div>
            <div className="workflow-grid"><div className="workflow-card"><span className="workflow-index">01</span><h3>Baseline</h3><p>Enter your factory, process, energy, material and waste data in a guided flow.</p><a href="#method">Explore intake ↗</a></div><div className="workflow-card dark"><span className="workflow-index">02</span><h3>Diagnose</h3><p>Rank hotspots by contribution so your team knows where attention creates leverage.</p><a href="#signals">See signals ↗</a></div><div className="workflow-card"><span className="workflow-index">03</span><h3>Decide</h3><p>Compare circular alternatives with reduction, cost and payback in one workspace.</p><a href="#cta">Start deciding ↗</a></div></div>
          </section>
          <section className="proof-band"><div><span className="eyebrow">A calmer way to act</span><h2>Clarity for operators. Evidence for leadership.</h2></div><div className="proof-list"><span>✓ Traceable calculations</span><span>✓ Practical recommendations</span><span>✓ Fast enough for the next meeting</span></div></section>
          <section className="final-cta" id="cta"><div><span className="eyebrow">Ready when you are / 04</span><h2>Make your next carbon decision count.</h2><p>Start with the data you have. Build a better baseline as you go.</p></div><Link to="/onboarding" className="primary-btn">Start free assessment <span>↗</span></Link></section>
          <footer className="landing-footer"><Link to="/" className="brand"><span className="brand-mark" />CircularCarbon</Link><span>Carbon intelligence for the circular factory.</span><span className="mono">© 2026</span></footer>
        </main>
      </div>
    </div>
  );
}

export default HomePage;
