# Data Source Policy

Priority: OFFICIAL → verified free official API → approved research source → explicitly labeled proxy → unavailable.

FREE ACCESS != FREE STORAGE != FREE REDISTRIBUTION != VALIDATION GRADE.

Every dataset must ultimately preserve source, source_timestamp, first_known_timestamp, received_at, source_hash, normalizer_version, validator_version and quality_status.

Forbidden: silent forward fill, fabricated bars, unlabeled synthetic data, lookahead, timezone/session mismatch, or a proxy presented as canonical execution truth.

`config/data-source-registry.json` is deny-by-default. Unverified terms/rights mean ingestion is denied even when the capability category is known to exist.
