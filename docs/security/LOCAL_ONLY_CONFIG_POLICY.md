# Local-Only Configuration Policy

User paths, account metadata, credentials, certificates, paid/restricted data locations and proprietary SDK locations are local-only.

Committed config contains schemas/defaults/policy, never private values. Missing required private state must fail closed; the application must not search arbitrary filesystem locations for credentials.
