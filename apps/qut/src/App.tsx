import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { zhTW } from "./messages";

type BridgeState = "checking" | "connected" | "denied";

const navigation = [
  zhTW.nav.research,
  zhTW.nav.data,
  zhTW.nav.backtest,
  zhTW.nav.dataQa,
  zhTW.nav.strategyLab,
  zhTW.nav.news,
  zhTW.nav.portfolioSimulation,
  zhTW.nav.paperMock,
] as const;

const hardGates = [
  ["Yuanta integration", "Disabled / Not Authorized"],
  ["Live Trading", "Disabled / Not Authorized"],
  ["Packaging", "Not Authorized"],
  ["Release", "Not Authorized"],
] as const;

function App() {
  const [bridgeState, setBridgeState] = useState<BridgeState>("checking");

  useEffect(() => {
    let active = true;

    invoke<string>("get_shell_status")
      .then((status) => {
        if (!active) return;
        setBridgeState(
          status === "QROS_PHASE4_LOCAL_ONLY" ? "connected" : "denied",
        );
      })
      .catch(() => {
        if (active) setBridgeState("denied");
      });

    return () => {
      active = false;
    };
  }, []);

  const bridgeLabel =
    bridgeState === "checking"
      ? zhTW.bridgeChecking
      : bridgeState === "connected"
        ? zhTW.bridgeConnected
        : zhTW.bridgeDenied;

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">{zhTW.phase}</p>
          <h1>{zhTW.appTitle}</h1>
        </div>
        <span className="local-badge">{zhTW.localOnly}</span>
      </header>

      <section className="notice" aria-label="Phase 4 scope">
        <strong>{zhTW.scopeNotice}</strong>
        <span>{zhTW.noNetwork}</span>
      </section>

      <div className="layout">
        <nav className="panel" aria-label={zhTW.navigation}>
          <h2>{zhTW.navigation}</h2>
          <ul className="nav-list">
            {navigation.map((item) => (
              <li key={item}>
                <button type="button" disabled>
                  {item}
                  <span>Phase 5+</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>

        <section className="content">
          <section className="panel">
            <h2>{zhTW.systemStatus}</h2>
            <div className="status-grid">
              <article className="status-card">
                <span>Desktop shell</span>
                <strong>Windows 11 x64 candidate</strong>
              </article>
              <article className="status-card">
                <span>Rust bridge</span>
                <strong data-state={bridgeState}>{bridgeLabel}</strong>
              </article>
              <article className="status-card">
                <span>Network</span>
                <strong>Local-only / no production endpoint</strong>
              </article>
              <article className="status-card">
                <span>WebView</span>
                <strong>System WebView2 Evergreen</strong>
              </article>
            </div>
          </section>

          <section className="panel">
            <h2>{zhTW.hardGates}</h2>
            <div className="gate-list">
              {hardGates.map(([name, status]) => (
                <article className="gate-row" key={name}>
                  <span>{name}</span>
                  <strong>{status}</strong>
                </article>
              ))}
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}

export default App;
