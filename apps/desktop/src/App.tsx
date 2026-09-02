const hardGates = [
  ["封裝", "DENY"],
  ["發佈", "DENY"],
  ["元大整合", "DENY"],
  ["真實交易", "DENY"],
] as const;

export default function App() {
  return (
    <main className="shell" aria-label="Jerry QROS Next 桌面工作站">
      <header className="topbar">
        <div>
          <p className="eyebrow">Jerry QROS Next</p>
          <h1>個人量化研究與交易工作站</h1>
        </div>
        <span className="candidate">Phase 4 implementation candidate</span>
      </header>

      <section className="panel" aria-labelledby="status-heading">
        <h2 id="status-heading">本機研究殼層</h2>
        <p>
          此畫面只驗證 Windows-first、zh-TW-first 的本機靜態桌面殼層。
          尚未接入 broker、網路服務或策略執行控制。
        </p>
      </section>

      <section className="gate-grid" aria-label="安全閘門">
        {hardGates.map(([label, state]) => (
          <article className="gate" key={label}>
            <span>{label}</span>
            <strong>{state}</strong>
          </article>
        ))}
      </section>

      <footer>
        UNKNOWN = DENY · Local static SPA · No remote content
      </footer>
    </main>
  );
}
