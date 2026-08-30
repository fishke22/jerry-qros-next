# Jerry QROS Next Architecture Baseline

> Authority: `deep-research-report.md` in the ChatGPT Project is the sole authoritative architecture/policy specification. This repository file is an implementation index, not a replacement specification.

## Target
Windows 11 x64 first; local-first; single-user first; zh-TW first; zero-extra-cost; evidence-driven; fail-closed; full-provenance; license-aware.

## Canonical architecture
```text
Windows 11 x64
  ↓
QUT Desktop — Tauri 2 + React + TypeScript
  ↓
QROS Local Application Layer
  ├─ Research / Strategy Lab
  ├─ DataHub
  ├─ Internal AI API
  ├─ Audit / Provenance
  ├─ Safety / Risk
  └─ LEAN Adapter
  ↓
QuantConnect LEAN
  ↓
Deterministic Safety Gate
  ↓
BrokerAdapter
  ├─ MockBrokerAdapter
  ├─ PaperBrokerAdapter
  └─ YuantaBrokerAdapter (FINAL / OPTIONAL / NOT AUTHORIZED)
```

## Invariants
Stable Core + Replaceable Adapters + Versioned Contracts + One Quant Truth + One Deterministic Execution Gate + Local-First AI + Official-First Data + zh-TW First UI + Fail-Closed Safety + Full Provenance + License-Aware Architecture + Zero-Cost Hard Gate + Packaging Hard Gate.

## Current non-goals
No second canonical quant truth. No mandatory Day-1 NATS/Perspective/MLflow/Qdrant/vLLM/OpenLLM/BentoML. No Yuanta access. No live broker path. No installer/release/updater. No strategy/alpha promotion from `fishke22/jerry-backtest-lab`.

Architecture drift path: Evidence → ADR → Proposed Amendment → Tests → user approval.
