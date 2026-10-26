# Engineering Onboarding

## Week 1 — Setup

New engineers receive their laptop pre-configured on their first day. The setup includes:

- Company SSO configured (Okta)
- VPN client installed (Tailscale)
- Development environment: Docker Desktop, VSCode, Git, Node 22, Python 3.12
- Access to GitHub organization `acme-eng`
- Access to internal docs portal (docs.acme.local)

By end of Week 1, every new engineer must:

1. Complete security training (90 min)
2. Set up 2FA on all company accounts
3. Clone and run the "hello-world" service locally
4. Deploy a change to the staging environment
5. Submit their first PR (can be documentation)

## Week 2-4 — Pairing

Every new engineer is paired with a buddy from a different team. The buddy:

- Does daily 30-min check-ins for the first 2 weeks
- Then weekly 1-on-1s for the following 2 weeks
- Reviews first 5 PRs together
- Introduces the engineer to the on-call rotation (shadow only — no primary rotation in the first 3 months)

## Tech stack

Core services:
- **Backend**: Python 3.12, FastAPI, PostgreSQL 16 (asyncpg), Redis 7
- **Frontend**: React 19, TypeScript, Vite
- **Infra**: AWS (us-east-1), Terraform, Kubernetes (EKS)
- **Observability**: Datadog, Sentry, OpenTelemetry
- **CI/CD**: GitHub Actions, ArgoCD

Database access from production is logged and audited. Read-only replicas are available for engineers via the internal `db-proxy` service.

## Code review

Every PR requires at least 1 approval. PRs touching:
- Database migrations: 2 approvals (one from senior)
- Authentication / authorization: 2 approvals (one from security team)
- Public API surface: 2 approvals (one from API tech lead)

All PRs run the automated test suite in CI. PRs with less than 80% test coverage on new code are blocked.

## On-call

New engineers do not go on primary rotation during their first 3 months. After 3 months, they shadow 2 on-call shifts with a senior before being added to the rotation.

The on-call rotation is weekly, Monday to Monday. On-call engineers receive a R$500 compensation per shift, plus overtime pay for incidents during off-hours.
