# Legacy D:\QROS Donor Assessment

Date: 2026-08-31  
Mode: read-only, selective, non-Yuanta donor assessment.

## Decision

`D:\QROS` is a mixed-trust legacy workspace and MUST NOT be uploaded wholesale to the public canonical repository.

Top-level inventory showed private/restricted-risk zones including:

- `secrets/`
- `data/personal_licensed/`
- `data/yuanta_*/`
- `lib/YuantaSparkAPI/`
- `local_vendor/yuanta_spark_api/`
- `integrations/yuanta/`
- broker-connected tests/scripts/logs
- local caches, virtual environments and Git history

Therefore:

- whole repository upload = DENY
- legacy Git history import = DENY
- direct runtime migration = DENY
- selective donor review = ALLOW only for explicitly non-Yuanta paths
- every promoted concept is independently redesigned/tested against QROS Next authority

`D:\YUANTA_AUTOPILOT` was NOT accessed or inventoried. Its boundary remains DENY until explicit user authorization for Yuanta SPARK integration.

## Whitelist assessment

Reviewed candidate areas:

- `src/data_foundation/`
- `src/data_quality/`
- `src/lineage/`
- `src/pit/`
- `src/universe/`
- `fixtures_synthetic/`
- `tools/provenance/`
- selected `docs/contracts/`

A 56-file text scan found no GitHub/OpenAI/AWS provider-key pattern and no private-key header. Files mentioning Yuanta/SPARK or secret/token/certificate concepts were excluded from promotion review rather than assumed safe.

## Methods retained as evidence

Representative safe donor hashes:

- `src/data_foundation/c_validation_bridge.py` — `53ba859216adf53f52aad03606a1c00afb528e7cae3b6817ab52106a62cd23f3`
- `src/data_quality/schema_consistency_contract.py` — `cf3ecd4f302f3c69890060bf47092dc443e034be293901238aaed0baaa60164d`
- `src/lineage/lineage_schema.py` — `abbc118e0ea6a749fe55571e30e459a38c99f31e7be346d3eedfa470aeb28001`
- `src/pit/pit_schema.py` — `f236a271834f3a2ada189e4e8a354b0dfea8bc3ed7c8f07f33ea4947efec42e1`
- `src/universe/universe_schema.py` — `4164c9f25a4032f3199ceb17c70cf900825d6c1810159450d48c66e878c5122e`
- `tools/provenance/validated_epoch_builder.py` — `c88db307d2a8d91c1215c6bf865100d89c1333718d8c3cb178fe134097781c48`

Useful donor semantics:

- lineage records code revision, config hash, source checksums and output checksum;
- PIT availability separates data date, release/availability time and earliest usable time;
- universe membership is effective-dated to reduce survivorship bias;
- validation classifications are review-only and never open gates automatically;
- provenance candidate selection is explicit/allowlisted rather than inherited from an untrusted historical index.

## Phase 1 promotion outcome

No legacy Python file was copied into QROS Next runtime.

The methods above were independently expressed as new versioned JSON contracts:

- `data-receipt/v1`
- `provenance-record/v1`
- `pit-availability/v1`
- `universe-membership/v1`
- `validation-result/v1`

This gives future cloud/mobile sessions the required semantics without making the new system depend on the legacy workspace.
