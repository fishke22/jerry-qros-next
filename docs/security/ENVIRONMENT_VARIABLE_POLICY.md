# Environment Variable Policy

No secret values in committed `.env` files. `.env.example` may contain names and non-secret placeholders only. Environment variables never override authorization gates. Future approved credentials must remain local-only and redacted. Phase 0 CI requires no repository secrets.
