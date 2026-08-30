# Secret Scanning Policy

Layers:
1. Preventive `.gitignore`.
2. Repository policy validator scans prohibited file types and common token/private-key patterns.
3. GitHub public-repository secret scanning is a free platform control; repository user-alert/push-protection configuration must be verified before claiming enabled.
4. Human diff review remains mandatory.

A scan PASS means no configured pattern was found; it is not proof that no secret exists.
