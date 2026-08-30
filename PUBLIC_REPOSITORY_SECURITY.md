# Public Repository Security Model

Deleting a later commit does not make a leaked secret safe.

GitHub may contain source, sanitized fixtures, policy, reproducible build metadata and public-rights-compatible artifacts only.

Local/private boundary only: credentials/tokens/passwords/cookies, broker identifiers, certificates/private keys, proprietary broker SDKs, restricted or paid raw market data, user-specific local config.

Controls:
1. `.gitignore`.
2. `scripts/validate_policies.py` for prohibited files and known secret patterns.
3. GitHub public-repository secret scanning is a free platform capability; repository alert/push-protection configuration must still be verified before claiming it enabled.
4. Fixtures must be synthetic or rights-compatible and sanitized.
5. Logs must be redacted before commit.
